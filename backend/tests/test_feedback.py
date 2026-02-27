"""Tests Phase 8 — Feedback utilisateur (suggestions & rapports de bugs).

Couvre :
- Soumission suggestion et bug_report
- Validation (type invalide, titre trop long, description trop longue)
- Auth (401 sans clé)
- GET /feedback/mine
- Admin : liste, détail, mise à jour statut
- Non-admin ne peut pas accéder à admin/feedback
"""
from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.api_key_repository import api_key_repository
from app.repositories.user_repository import user_repository

BASE = "/feedback"
ADMIN_BASE = "/admin/feedback"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_admin(db: AsyncSession):
    user = await user_repository.create(
        db,
        first_name="Admin",
        last_name="Test",
        email=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        role="admin",
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, "admin-device")
    await db.commit()
    return user, plain_key


@pytest_asyncio.fixture
async def admin_key(db: AsyncSession) -> str:
    _, key = await _make_admin(db)
    return key


@pytest_asyncio.fixture
async def coach_key(db: AsyncSession) -> str:
    user = await user_repository.create(
        db,
        first_name="CoachFB",
        last_name="Test",
        email=f"coachfb_{uuid.uuid4().hex[:8]}@test.com",
        role="coach",
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, "coach-device")
    await db.commit()
    return plain_key


async def _post_feedback(client: AsyncClient, api_key: str, payload: dict):
    return await client.post(f"{BASE}/", json=payload, headers={"X-API-Key": api_key})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_submit_suggestion_ok(client: AsyncClient, coach_api_key: str):
    """✅ POST /feedback type=suggestion → 201."""
    resp = await _post_feedback(client, coach_api_key, {
        "type": "suggestion",
        "title": "Améliorer le tableau de bord",
        "description": "Afficher les stats en temps réel",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "suggestion"
    assert data["status"] == "pending"
    assert data["title"] == "Améliorer le tableau de bord"
    assert "id" in data


@pytest.mark.asyncio
async def test_submit_bug_report_ok(client: AsyncClient, coach_api_key: str):
    """✅ POST /feedback type=bug_report → 201."""
    resp = await _post_feedback(client, coach_api_key, {
        "type": "bug_report",
        "title": "Crash sur l'écran de réservation",
        "description": "L'application plante quand on clique sur Réserver",
        "app_version": "1.2.3",
        "platform": "ios",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "bug_report"
    assert data["app_version"] == "1.2.3"
    assert data["platform"] == "ios"


@pytest.mark.asyncio
async def test_submit_invalid_type(client: AsyncClient, coach_api_key: str):
    """❌ type='other' → 422."""
    resp = await _post_feedback(client, coach_api_key, {
        "type": "other",
        "title": "Titre",
        "description": "Description",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_title_too_long(client: AsyncClient, coach_api_key: str):
    """❌ title > 200 chars → 422."""
    resp = await _post_feedback(client, coach_api_key, {
        "type": "suggestion",
        "title": "A" * 201,
        "description": "Description normale",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_description_too_long(client: AsyncClient, coach_api_key: str):
    """❌ description > 5000 chars → 422."""
    resp = await _post_feedback(client, coach_api_key, {
        "type": "bug_report",
        "title": "Titre normal",
        "description": "X" * 5001,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_no_auth(client: AsyncClient):
    """❌ POST sans API key → 401."""
    resp = await client.post(f"{BASE}/", json={
        "type": "suggestion",
        "title": "Titre",
        "description": "Description",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_my_feedbacks(client: AsyncClient, coach_api_key: str):
    """✅ GET /feedback/mine → mes feedbacks."""
    # Soumettre deux feedbacks
    await _post_feedback(client, coach_api_key, {
        "type": "suggestion", "title": "Idée 1", "description": "Détail de l'idée 1",
    })
    await _post_feedback(client, coach_api_key, {
        "type": "bug_report", "title": "Bug 1", "description": "Description du bug 1",
    })

    resp = await client.get(f"{BASE}/mine", headers={"X-API-Key": coach_api_key})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    types = {f["type"] for f in data}
    assert "suggestion" in types
    assert "bug_report" in types


@pytest.mark.asyncio
async def test_admin_list_feedbacks(client: AsyncClient, coach_api_key: str, admin_key: str):
    """✅ GET /admin/feedback → liste tous les feedbacks."""
    await _post_feedback(client, coach_api_key, {
        "type": "suggestion", "title": "Titre", "description": "Détails",
    })

    resp = await client.get(ADMIN_BASE, headers={"X-API-Key": admin_key})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_admin_update_status(client: AsyncClient, coach_api_key: str, admin_key: str):
    """✅ PATCH /admin/feedback/{id} {status: 'reviewing'} → 200."""
    create_resp = await _post_feedback(client, coach_api_key, {
        "type": "suggestion", "title": "Idée", "description": "Détails complets",
    })
    feedback_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"{ADMIN_BASE}/{feedback_id}",
        json={"status": "reviewing", "admin_note": "En cours d'analyse"},
        headers={"X-API-Key": admin_key},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["status"] == "reviewing"
    assert data["admin_note"] == "En cours d'analyse"


@pytest.mark.asyncio
async def test_non_admin_cannot_list_all(client: AsyncClient, coach_key: str):
    """❌ Coach → GET /admin/feedback → 403."""
    resp = await client.get(ADMIN_BASE, headers={"X-API-Key": coach_key})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_get_feedback_detail(client: AsyncClient, coach_api_key: str, admin_key: str):
    """✅ GET /admin/feedback/{id} → détail du feedback."""
    create_resp = await _post_feedback(client, coach_api_key, {
        "type": "bug_report", "title": "Bug critique", "description": "Détails du bug critique",
    })
    feedback_id = create_resp.json()["id"]

    resp = await client.get(f"{ADMIN_BASE}/{feedback_id}", headers={"X-API-Key": admin_key})
    assert resp.status_code == 200
    assert resp.json()["id"] == feedback_id


@pytest.mark.asyncio
async def test_admin_get_feedback_not_found(client: AsyncClient, admin_key: str):
    """❌ GET /admin/feedback/{id} inexistant → 404."""
    resp = await client.get(f"{ADMIN_BASE}/{uuid.uuid4()}", headers={"X-API-Key": admin_key})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_mine_isolation(
    client: AsyncClient, coach_api_key: str, client_api_key: str
):
    """✅ /feedback/mine ne retourne que les feedbacks de l'utilisateur courant."""
    await _post_feedback(client, coach_api_key, {
        "type": "suggestion", "title": "Du coach", "description": "Détails coach",
    })
    await _post_feedback(client, client_api_key, {
        "type": "bug_report", "title": "Du client", "description": "Détails client",
    })

    coach_resp = await client.get(f"{BASE}/mine", headers={"X-API-Key": coach_api_key})
    client_resp = await client.get(f"{BASE}/mine", headers={"X-API-Key": client_api_key})

    assert len(coach_resp.json()) == 1
    assert len(client_resp.json()) == 1
    assert coach_resp.json()[0]["title"] == "Du coach"
    assert client_resp.json()[0]["title"] == "Du client"

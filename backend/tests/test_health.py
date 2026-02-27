"""Tests Phase 8 — Paramètres de santé, logs, partage.

Couvre :
- GET /health/parameters (liste paramètres)
- POST /health/logs (enregistrer mesure)
- GET /health/logs (mon historique)
- DELETE /health/logs/{id}
- GET /health/sharing/{coach_id}
- PATCH /health/sharing/{coach_id}
- GET /health/clients/{client_id}/logs (coach)
- Admin : POST /admin/health/parameters
- Auth 401
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_parameter import HealthParameter
from app.repositories.api_key_repository import api_key_repository
from app.repositories.user_repository import user_repository

BASE = "/health"


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

async def _make_user(db: AsyncSession, role: str):
    user = await user_repository.create(
        db,
        first_name=role.capitalize(),
        last_name="Health",
        email=f"{role}_h_{uuid.uuid4().hex[:8]}@test.com",
        role=role,
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, f"{role}-device")
    await db.commit()
    return user, plain_key


@pytest_asyncio.fixture
async def health_params(db: AsyncSession):
    """Crée quelques paramètres de santé pour les tests (conftest utilise create_all, pas alembic)."""
    params = {}
    for slug, label_fr, unit in [
        ("weight_kg", "Poids", "kg"),
        ("body_fat_pct", "% Masse grasse", "%"),
        ("resting_heart_rate_bpm", "FC repos", "bpm"),
    ]:
        p = HealthParameter(
            slug=slug,
            label={"fr": label_fr, "en": label_fr},
            unit=unit,
            data_type="float",
            category="test",
            active=True,
            position=0,
        )
        db.add(p)
    await db.flush()
    await db.commit()
    result = await db.execute(select(HealthParameter))
    for p in result.scalars().all():
        params[p.slug] = p
    return params


@pytest_asyncio.fixture
async def coach_user_health(db: AsyncSession):
    user, key = await _make_user(db, "coach")
    return user, key


@pytest_asyncio.fixture
async def client_user_health(db: AsyncSession):
    user, key = await _make_user(db, "client")
    return user, key


@pytest_asyncio.fixture
async def admin_user_health(db: AsyncSession):
    user, key = await _make_user(db, "admin")
    return user, key


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


async def _log(client: AsyncClient, api_key: str, parameter_id, value: float):
    return await client.post(
        f"{BASE}/logs",
        json={
            "parameter_id": str(parameter_id),
            "value": value,
            "logged_at": _now_iso(),
        },
        headers={"X-API-Key": api_key},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_parameters(client: AsyncClient, coach_api_key: str, health_params):
    """✅ GET /health/parameters → liste non vide (seed via fixture)."""
    resp = await client.get(f"{BASE}/parameters", headers={"X-API-Key": coach_api_key})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 3
    slugs = {p["slug"] for p in data}
    assert "weight_kg" in slugs


@pytest.mark.asyncio
async def test_log_weight(client: AsyncClient, coach_api_key: str, health_params):
    """✅ POST /health/logs {parameter: weight_kg, value: 75.5} → 201."""
    param_id = health_params["weight_kg"].id
    resp = await _log(client, coach_api_key, param_id, 75.5)
    assert resp.status_code == 201
    data = resp.json()
    assert float(data["value"]) == pytest.approx(75.5, abs=0.01)
    assert data["parameter"]["slug"] == "weight_kg"


@pytest.mark.asyncio
async def test_log_invalid_parameter(client: AsyncClient, coach_api_key: str, health_params):
    """❌ paramètre inconnu → 422."""
    resp = await _log(client, coach_api_key, uuid.uuid4(), 75.5)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_my_logs(client: AsyncClient, coach_api_key: str, health_params):
    """✅ GET /health/logs → mes mesures."""
    param_id = health_params["weight_kg"].id
    await _log(client, coach_api_key, param_id, 80.0)
    await _log(client, coach_api_key, param_id, 79.5)

    resp = await client.get(f"{BASE}/logs", headers={"X-API-Key": coach_api_key})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_logs_filtered_by_param(client: AsyncClient, coach_api_key: str, health_params):
    """✅ filtre parameter_id → seul ce param retourné."""
    weight_id = health_params["weight_kg"].id
    fat_id = health_params["body_fat_pct"].id

    await _log(client, coach_api_key, weight_id, 80.0)
    await _log(client, coach_api_key, fat_id, 15.0)

    resp = await client.get(
        f"{BASE}/logs",
        params={"parameter_id": str(weight_id)},
        headers={"X-API-Key": coach_api_key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["parameter"]["slug"] == "weight_kg"


@pytest.mark.asyncio
async def test_delete_log(client: AsyncClient, coach_api_key: str, health_params):
    """✅ DELETE /health/logs/{id} → 204."""
    param_id = health_params["weight_kg"].id
    log_resp = await _log(client, coach_api_key, param_id, 77.0)
    log_id = log_resp.json()["id"]

    del_resp = await client.delete(
        f"{BASE}/logs/{log_id}",
        headers={"X-API-Key": coach_api_key},
    )
    assert del_resp.status_code == 204

    # Log is gone
    get_resp = await client.get(f"{BASE}/logs", headers={"X-API-Key": coach_api_key})
    assert get_resp.json() == []


@pytest.mark.asyncio
async def test_delete_other_user_log(client: AsyncClient, health_params, db: AsyncSession):
    """❌ DELETE log d'un autre utilisateur → 404."""
    _, key1 = await _make_user(db, "client")
    _, key2 = await _make_user(db, "client")
    param_id = health_params["weight_kg"].id

    log_resp = await _log(client, key1, param_id, 70.0)
    log_id = log_resp.json()["id"]

    # User 2 tries to delete user 1's log
    del_resp = await client.delete(
        f"{BASE}/logs/{log_id}",
        headers={"X-API-Key": key2},
    )
    assert del_resp.status_code == 404


@pytest.mark.asyncio
async def test_sharing_default_all_shared(
    client: AsyncClient, health_params, db: AsyncSession
):
    """✅ GET /health/sharing/{coach_id} → tous shared=True par défaut."""
    client_user, client_key = await _make_user(db, "client")
    coach_user, _ = await _make_user(db, "coach")

    resp = await client.get(
        f"{BASE}/sharing/{coach_user.id}",
        headers={"X-API-Key": client_key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(health_params)
    assert all(item["shared"] is True for item in data)


@pytest.mark.asyncio
async def test_update_sharing_hide_param(
    client: AsyncClient, health_params, db: AsyncSession
):
    """✅ PATCH sharing → shared=False pour weight_kg."""
    client_user, client_key = await _make_user(db, "client")
    coach_user, _ = await _make_user(db, "coach")
    weight_id = health_params["weight_kg"].id

    resp = await client.patch(
        f"{BASE}/sharing/{coach_user.id}",
        json={"updates": [{"parameter_id": str(weight_id), "shared": False}]},
        headers={"X-API-Key": client_key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["parameter_id"] == str(weight_id)
    assert data[0]["shared"] is False


@pytest.mark.asyncio
async def test_coach_cannot_see_hidden_param(
    client: AsyncClient, health_params, db: AsyncSession
):
    """✅ GET /health/clients/{id}/logs → weight_kg masqué."""
    client_user, client_key = await _make_user(db, "client")
    coach_user, coach_key = await _make_user(db, "coach")
    weight_id = health_params["weight_kg"].id
    fat_id = health_params["body_fat_pct"].id

    # Log both
    await _log(client, client_key, weight_id, 70.0)
    await _log(client, client_key, fat_id, 20.0)

    # Hide weight from coach
    await client.patch(
        f"{BASE}/sharing/{coach_user.id}",
        json={"updates": [{"parameter_id": str(weight_id), "shared": False}]},
        headers={"X-API-Key": client_key},
    )

    # Coach fetches client logs
    resp = await client.get(
        f"{BASE}/clients/{client_user.id}/logs",
        headers={"X-API-Key": coach_key},
    )
    assert resp.status_code == 200
    data = resp.json()
    slugs = [log["parameter"]["slug"] for log in data]
    assert "weight_kg" not in slugs
    assert "body_fat_pct" in slugs


@pytest.mark.asyncio
async def test_coach_can_see_shared_params(
    client: AsyncClient, health_params, db: AsyncSession
):
    """✅ paramètre shared=True → visible par le coach."""
    client_user, client_key = await _make_user(db, "client")
    coach_user, coach_key = await _make_user(db, "coach")
    weight_id = health_params["weight_kg"].id

    await _log(client, client_key, weight_id, 72.0)

    # No sharing update → default shared=True
    resp = await client.get(
        f"{BASE}/clients/{client_user.id}/logs",
        headers={"X-API-Key": coach_key},
    )
    assert resp.status_code == 200
    data = resp.json()
    slugs = [log["parameter"]["slug"] for log in data]
    assert "weight_kg" in slugs


@pytest.mark.asyncio
async def test_no_auth_health(client: AsyncClient):
    """❌ Endpoints sans API key → 401."""
    r1 = await client.get(f"{BASE}/parameters")
    r2 = await client.get(f"{BASE}/logs")
    assert r1.status_code == 401
    assert r2.status_code == 401


@pytest.mark.asyncio
async def test_client_can_log(client: AsyncClient, client_api_key: str, health_params):
    """✅ client aussi peut logger."""
    param_id = health_params["weight_kg"].id
    resp = await _log(client, client_api_key, param_id, 65.0)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_coach_can_log(client: AsyncClient, coach_api_key: str, health_params):
    """✅ coach peut aussi logger ses propres mesures."""
    param_id = health_params["body_fat_pct"].id
    resp = await _log(client, coach_api_key, param_id, 18.0)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_admin_add_parameter(client: AsyncClient, health_params, db: AsyncSession):
    """✅ POST /admin/health/parameters → 201."""
    _, admin_key = await _make_user(db, "admin")

    resp = await client.post(
        "/admin/health/parameters",
        json={
            "slug": "hydration_level",
            "label": {"fr": "Hydratation", "en": "Hydration"},
            "unit": "%",
            "data_type": "float",
            "category": "other",
            "position": 99,
        },
        headers={"X-API-Key": admin_key},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "hydration_level"
    assert data["active"] is True


@pytest.mark.asyncio
async def test_admin_soft_delete_parameter(client: AsyncClient, health_params, db: AsyncSession):
    """✅ DELETE /admin/health/parameters/{id} → soft delete (active=False)."""
    _, admin_key = await _make_user(db, "admin")
    param_id = health_params["weight_kg"].id

    resp = await client.delete(
        f"/admin/health/parameters/{param_id}",
        headers={"X-API-Key": admin_key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["active"] is False


@pytest.mark.asyncio
async def test_non_coach_cannot_access_client_logs(
    client: AsyncClient, client_api_key: str, health_params, db: AsyncSession
):
    """❌ Client ne peut pas accéder aux logs d'un autre client."""
    other_user, _ = await _make_user(db, "client")

    resp = await client.get(
        f"{BASE}/clients/{other_user.id}/logs",
        headers={"X-API-Key": client_api_key},
    )
    assert resp.status_code == 403

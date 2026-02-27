"""Tests Phase 9 — Liens d'enrôlement coach.

Couvre :
1.  test_coach_creates_token            POST /coaches/me/enrollment-tokens → 201 + enrollment_link
2.  test_coach_creates_token_with_label avec label + expires_at + max_uses
3.  test_client_cannot_create_token     client → 403
4.  test_list_tokens                    GET /coaches/me/enrollment-tokens → liste
5.  test_deactivate_token               DELETE → 204, token désactivé
6.  test_deactivate_other_coach_token   404
7.  test_get_enrollment_info_valid      GET /enroll/{token} → infos coach
8.  test_get_enrollment_info_invalid_token 404
9.  test_register_with_enrollment_token inscription avec token → coaching_relation créée
10. test_register_with_expired_token    inscription réussit même si token expiré
11. test_register_with_invalid_token    inscription réussit même si token invalide
12. test_max_uses_enforcement           après max_uses inscriptions, token désactivé
13. test_token_uses_count_incremented   uses_count += 1 après inscription
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coach_enrollment_token import CoachEnrollmentToken
from app.models.coaching_relation import CoachingRelation
from app.repositories.api_key_repository import api_key_repository
from app.repositories.enrollment_repository import create_token as repo_create_token
from app.repositories.user_repository import user_repository
from app.schemas.enrollment import EnrollmentTokenCreate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_user(db: AsyncSession, role: str):
    user = await user_repository.create(
        db,
        first_name=role.capitalize(),
        last_name="Enroll",
        email=f"{role}_e_{uuid.uuid4().hex[:8]}@test.com",
        role=role,
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, f"{role}-device")
    await db.commit()
    return user, plain_key


async def _create_enrollment_token(db: AsyncSession, coach_id: uuid.UUID, **kwargs):
    """Crée un token d'enrôlement directement en DB."""
    data = EnrollmentTokenCreate(
        label=kwargs.get("label"),
        expires_at=kwargs.get("expires_at"),
        max_uses=kwargs.get("max_uses"),
    )
    token = await repo_create_token(db, coach_id, data)
    await db.commit()
    return token


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_coach_creates_token(client: AsyncClient, db: AsyncSession):
    """1. POST /coaches/me/enrollment-tokens → 201 avec enrollment_link."""
    coach, key = await _make_user(db, "coach")
    resp = await client.post(
        "/coaches/me/enrollment-tokens",
        json={},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["enrollment_link"].startswith("mycoach://enroll/")
    assert data["active"] is True
    assert data["uses_count"] == 0


@pytest.mark.asyncio
async def test_coach_creates_token_with_label(client: AsyncClient, db: AsyncSession):
    """2. avec label + expires_at + max_uses."""
    coach, key = await _make_user(db, "coach")
    expires = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    resp = await client.post(
        "/coaches/me/enrollment-tokens",
        json={"label": "Groupe yoga janvier", "expires_at": expires, "max_uses": 10},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["label"] == "Groupe yoga janvier"
    assert data["max_uses"] == 10
    assert data["expires_at"] is not None


@pytest.mark.asyncio
async def test_client_cannot_create_token(client: AsyncClient, db: AsyncSession):
    """3. client → 403."""
    _, key = await _make_user(db, "client")
    resp = await client.post(
        "/coaches/me/enrollment-tokens",
        json={},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_tokens(client: AsyncClient, db: AsyncSession):
    """4. GET /coaches/me/enrollment-tokens → liste."""
    coach, key = await _make_user(db, "coach")
    # Créer 2 tokens
    await _create_enrollment_token(db, coach.id, label="Token A")
    await _create_enrollment_token(db, coach.id, label="Token B")

    resp = await client.get("/coaches/me/enrollment-tokens", headers={"X-API-Key": key})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    labels = [t["label"] for t in data]
    assert "Token A" in labels
    assert "Token B" in labels


@pytest.mark.asyncio
async def test_deactivate_token(client: AsyncClient, db: AsyncSession):
    """5. DELETE → 204, token désactivé."""
    coach, key = await _make_user(db, "coach")
    token = await _create_enrollment_token(db, coach.id)

    resp = await client.delete(
        f"/coaches/me/enrollment-tokens/{token.id}",
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 204

    # Vérifier que le token est désactivé en base
    await db.refresh(token)
    assert token.active is False


@pytest.mark.asyncio
async def test_deactivate_other_coach_token(client: AsyncClient, db: AsyncSession):
    """6. Un coach ne peut pas désactiver le token d'un autre coach → 404."""
    coach1, key1 = await _make_user(db, "coach")
    coach2, key2 = await _make_user(db, "coach")
    token = await _create_enrollment_token(db, coach2.id)

    resp = await client.delete(
        f"/coaches/me/enrollment-tokens/{token.id}",
        headers={"X-API-Key": key1},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_enrollment_info_valid(client: AsyncClient, db: AsyncSession):
    """7. GET /enroll/{token} → infos coach."""
    coach, _ = await _make_user(db, "coach")
    token = await _create_enrollment_token(db, coach.id, label="Offre spéciale")

    resp = await client.get(f"/enroll/{token.token}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["coach_id"] == str(coach.id)
    assert data["coach_first_name"] == "Coach"
    assert data["valid"] is True
    assert data["label"] == "Offre spéciale"


@pytest.mark.asyncio
async def test_get_enrollment_info_invalid_token(client: AsyncClient, db: AsyncSession):
    """8. Token inexistant → 404."""
    resp = await client.get("/enroll/token_inexistant_123456789")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_register_with_enrollment_token(client: AsyncClient, db: AsyncSession):
    """9. Inscription avec token valide → coaching_relation créée."""
    coach, _ = await _make_user(db, "coach")
    token = await _create_enrollment_token(db, coach.id)

    new_email = f"new_client_{uuid.uuid4().hex[:8]}@test.com"
    resp = await client.post(
        "/auth/register",
        json={
            "first_name": "Nouveau",
            "last_name": "Client",
            "email": new_email,
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "client",
            "enrollment_token": token.token,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    new_user_id = uuid.UUID(data["user"]["id"])

    # Vérifier en DB que la relation coach-client existe
    result = await db.execute(
        select(CoachingRelation).where(
            CoachingRelation.coach_id == coach.id,
            CoachingRelation.client_id == new_user_id,
        )
    )
    relation = result.scalar_one_or_none()
    assert relation is not None
    assert relation.status == "active"


@pytest.mark.asyncio
async def test_register_with_expired_token(client: AsyncClient, db: AsyncSession):
    """10. Inscription réussit même si token expiré (pas de blocage)."""
    coach, _ = await _make_user(db, "coach")
    expires = datetime.now(timezone.utc) - timedelta(hours=1)
    token = await _create_enrollment_token(db, coach.id, expires_at=expires)

    new_email = f"new_expired_{uuid.uuid4().hex[:8]}@test.com"
    resp = await client.post(
        "/auth/register",
        json={
            "first_name": "Nouveau",
            "last_name": "Client",
            "email": new_email,
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "client",
            "enrollment_token": token.token,
        },
    )
    # L'inscription doit réussir (201) même si le token est expiré
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_register_with_invalid_token(client: AsyncClient, db: AsyncSession):
    """11. Inscription réussit même si token invalide."""
    new_email = f"new_invalid_{uuid.uuid4().hex[:8]}@test.com"
    resp = await client.post(
        "/auth/register",
        json={
            "first_name": "Nouveau",
            "last_name": "Client",
            "email": new_email,
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "client",
            "enrollment_token": "token_qui_nexiste_pas",
        },
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_max_uses_enforcement(client: AsyncClient, db: AsyncSession):
    """12. Après max_uses inscriptions, token désactivé."""
    coach, _ = await _make_user(db, "coach")
    token = await _create_enrollment_token(db, coach.id, max_uses=2)
    token_str = token.token
    token_id = token.id

    # 2 inscriptions → uses_count = 2 = max_uses → désactivé
    for i in range(2):
        email = f"max_uses_{i}_{uuid.uuid4().hex[:8]}@test.com"
        resp = await client.post(
            "/auth/register",
            json={
                "first_name": "Client",
                "last_name": f"Num{i}",
                "email": email,
                "password": "Password1",
                "confirm_password": "Password1",
                "role": "client",
                "enrollment_token": token_str,
            },
        )
        assert resp.status_code == 201

    # Re-charger le token depuis la DB (expire le cache de la session)
    db.expire_all()
    result = await db.execute(
        select(CoachEnrollmentToken).where(CoachEnrollmentToken.id == token_id)
    )
    refreshed = result.scalar_one_or_none()
    assert refreshed is not None
    assert refreshed.uses_count == 2
    assert refreshed.active is False


@pytest.mark.asyncio
async def test_token_uses_count_incremented(client: AsyncClient, db: AsyncSession):
    """13. uses_count += 1 après inscription."""
    coach, _ = await _make_user(db, "coach")
    token = await _create_enrollment_token(db, coach.id)
    token_id = token.id
    initial_count = token.uses_count  # should be 0

    new_email = f"uses_count_{uuid.uuid4().hex[:8]}@test.com"
    resp = await client.post(
        "/auth/register",
        json={
            "first_name": "Nouveau",
            "last_name": "Client",
            "email": new_email,
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "client",
            "enrollment_token": token.token,
        },
    )
    assert resp.status_code == 201

    # Re-charger le token pour vérifier uses_count (expire le cache de la session)
    db.expire_all()
    result = await db.execute(
        select(CoachEnrollmentToken).where(CoachEnrollmentToken.id == token_id)
    )
    refreshed = result.scalar_one_or_none()
    assert refreshed is not None
    assert refreshed.uses_count == initial_count + 1

"""Tests — Profil utilisateur (genre, année de naissance, avatar par défaut).

Couvre :
1.  test_update_gender                  PATCH /users/me/profile {gender: "male"} → 200
2.  test_update_birth_year              PATCH {birth_year: 1990} → 200
3.  test_invalid_gender                 gender="unknown" → 422
4.  test_invalid_birth_year_future      birth_year=2100 → 422
5.  test_invalid_birth_year_too_old     birth_year=1800 → 422
6.  test_default_avatar_no_gender       user sans avatar ni genre → default_neutral
7.  test_default_avatar_male            user genre=male, pas de photo → default_male
8.  test_avatar_custom_overrides_default user avec avatar_url défini → resolved_avatar_url=avatar_url
"""
from __future__ import annotations

import uuid
import datetime as dt

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.api_key_repository import api_key_repository
from app.repositories.user_repository import user_repository
from app.schemas.common import resolve_avatar_url


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _make_user(db: AsyncSession, role: str = "client") -> tuple:
    user = await user_repository.create(
        db,
        first_name="Profile",
        last_name="Test",
        email=f"profile_{uuid.uuid4().hex[:8]}@test.com",
        role=role,
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, "device")
    await db.commit()
    return user, plain_key


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_gender(client: AsyncClient, db: AsyncSession):
    """1. PATCH /users/me/profile {gender: "male"} → 200."""
    user, key = await _make_user(db)
    resp = await client.patch(
        "/users/me/profile",
        json={"gender": "male"},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["gender"] == "male"


@pytest.mark.asyncio
async def test_update_birth_year(client: AsyncClient, db: AsyncSession):
    """2. PATCH {birth_year: 1990} → 200."""
    user, key = await _make_user(db)
    resp = await client.patch(
        "/users/me/profile",
        json={"birth_year": 1990},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["birth_year"] == 1990


@pytest.mark.asyncio
async def test_invalid_gender(client: AsyncClient, db: AsyncSession):
    """3. gender="unknown" → 422."""
    user, key = await _make_user(db)
    resp = await client.patch(
        "/users/me/profile",
        json={"gender": "unknown"},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_birth_year_future(client: AsyncClient, db: AsyncSession):
    """4. birth_year=2100 → 422."""
    user, key = await _make_user(db)
    resp = await client.patch(
        "/users/me/profile",
        json={"birth_year": 2100},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_birth_year_too_old(client: AsyncClient, db: AsyncSession):
    """5. birth_year=1800 → 422."""
    user, key = await _make_user(db)
    resp = await client.patch(
        "/users/me/profile",
        json={"birth_year": 1800},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_default_avatar_no_gender(client: AsyncClient, db: AsyncSession):
    """6. user sans avatar ni genre → resolved_avatar_url = default_neutral."""
    user, key = await _make_user(db)

    # Vérifier via la fonction utilitaire
    resolved = resolve_avatar_url(None, None)
    assert resolved == "/static/avatars/default_neutral.svg"

    # Vérifier via l'API (GET /auth/me)
    resp = await client.get("/auth/me", headers={"X-API-Key": key})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["resolved_avatar_url"] == "/static/avatars/default_neutral.svg"


@pytest.mark.asyncio
async def test_default_avatar_male(client: AsyncClient, db: AsyncSession):
    """7. user genre=male, pas de photo → resolved_avatar_url = default_male."""
    user, key = await _make_user(db)

    # Mettre à jour le genre
    resp = await client.patch(
        "/users/me/profile",
        json={"gender": "male"},
        headers={"X-API-Key": key},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["resolved_avatar_url"] == "/static/avatars/default_male.svg"

    # Vérifier via la fonction utilitaire
    assert resolve_avatar_url(None, "male") == "/static/avatars/default_male.svg"


@pytest.mark.asyncio
async def test_avatar_custom_overrides_default(client: AsyncClient, db: AsyncSession):
    """8. user avec avatar_url défini → resolved_avatar_url = avatar_url."""
    user, key = await _make_user(db)
    custom_url = "https://example.com/my_avatar.jpg"

    # Simuler un avatar custom via DB
    user.avatar_url = custom_url
    await db.commit()

    # Vérifier via la fonction utilitaire
    assert resolve_avatar_url(custom_url, None) == custom_url
    assert resolve_avatar_url(custom_url, "male") == custom_url

    # Vérifier via l'API
    resp = await client.get("/auth/me", headers={"X-API-Key": key})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["resolved_avatar_url"] == custom_url

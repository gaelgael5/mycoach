"""Tests — Blocklist domaines email jetables."""
from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import blocked_domain_repository
from app.repositories.api_key_repository import api_key_repository
from app.repositories.user_repository import user_repository
from app.services.email_domain_service import extract_domain, BlockedDomainError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_admin(db: AsyncSession):
    """Crée un utilisateur admin + API key pour les tests."""
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


async def _make_coach(db: AsyncSession):
    """Crée un utilisateur coach + API key pour les tests."""
    user = await user_repository.create(
        db,
        first_name="Coach",
        last_name="Test",
        email=f"coach_{uuid.uuid4().hex[:8]}@test.com",
        role="coach",
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, "coach-device")
    await db.commit()
    return user, plain_key


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def seed_blocked_domains(db: AsyncSession):
    """Seed quelques domaines bloqués pour les tests."""
    for domain in ["yopmail.com", "mailinator.com", "tempmail.com", "guerrillamail.com"]:
        await blocked_domain_repository.add(db, domain, "Test")
    await db.commit()


@pytest_asyncio.fixture()
async def admin_headers(db: AsyncSession):
    """Headers API pour un admin."""
    _, plain_key = await _make_admin(db)
    return {"X-API-Key": plain_key}


@pytest_asyncio.fixture()
async def coach_headers(db: AsyncSession):
    """Headers API pour un coach."""
    _, plain_key = await _make_coach(db)
    return {"X-API-Key": plain_key}


# ---------------------------------------------------------------------------
# Test 1 — Inscription avec domaine bloqué → 422
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_with_blocked_domain_returns_422(client: AsyncClient, db: AsyncSession, seed_blocked_domains):
    resp = await client.post("/auth/register", json={
        "first_name": "Alice",
        "last_name": "Yop",
        "email": "alice@yopmail.com",
        "password": "Password1",
        "confirm_password": "Password1",
        "role": "client",
    })
    assert resp.status_code == 422, resp.text
    assert "yopmail.com" in resp.text


# ---------------------------------------------------------------------------
# Test 2 — Inscription avec domaine valide → 201
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_with_valid_domain_succeeds(client: AsyncClient, seed_blocked_domains):
    resp = await client.post("/auth/register", json={
        "first_name": "Bob",
        "last_name": "Valid",
        "email": f"bob_{uuid.uuid4().hex[:6]}@gmail.com",
        "password": "Password1",
        "confirm_password": "Password1",
        "role": "client",
    })
    assert resp.status_code == 201, resp.text


# ---------------------------------------------------------------------------
# Test 3 — Insensibilité à la casse
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_blocked_domain_check_is_case_insensitive(client: AsyncClient, db: AsyncSession, seed_blocked_domains):
    resp = await client.post("/auth/register", json={
        "first_name": "Charlie",
        "last_name": "Upper",
        "email": "USER@YOPMAIL.COM",
        "password": "Password1",
        "confirm_password": "Password1",
        "role": "client",
    })
    assert resp.status_code == 422, resp.text


# ---------------------------------------------------------------------------
# Test 4 — Plusieurs domaines bloqués, tous refusés
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_multiple_blocked_domains_all_rejected(client: AsyncClient, db: AsyncSession, seed_blocked_domains):
    blocked_emails = [
        f"user_{uuid.uuid4().hex[:4]}@mailinator.com",
        f"user_{uuid.uuid4().hex[:4]}@tempmail.com",
        f"user_{uuid.uuid4().hex[:4]}@guerrillamail.com",
    ]
    for email in blocked_emails:
        resp = await client.post("/auth/register", json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": "Password1",
            "confirm_password": "Password1",
            "role": "client",
        })
        assert resp.status_code == 422, f"Expected 422 for {email}, got {resp.status_code}"


# ---------------------------------------------------------------------------
# Test 5 — Admin liste les domaines bloqués (seed via fixture)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_list_blocked_domains(client: AsyncClient, db: AsyncSession, seed_blocked_domains, admin_headers):
    resp = await client.get("/admin/blocked-domains", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) > 0
    domains = [item["domain"] for item in data]
    assert "yopmail.com" in domains


# ---------------------------------------------------------------------------
# Test 6 — Admin ajoute un domaine → 201
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_add_domain(client: AsyncClient, db: AsyncSession, admin_headers):
    resp = await client.post("/admin/blocked-domains", headers=admin_headers, json={
        "domain": "spamtest-unique.com",
        "reason": "Test ajout",
    })
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["domain"] == "spamtest-unique.com"
    assert data["reason"] == "Test ajout"


# ---------------------------------------------------------------------------
# Test 7 — Doublon → 409
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_add_duplicate_domain(client: AsyncClient, db: AsyncSession, admin_headers):
    # Premier ajout
    r1 = await client.post("/admin/blocked-domains", headers=admin_headers, json={
        "domain": "doublon-test.com",
        "reason": "Premier",
    })
    assert r1.status_code == 201, r1.text

    # Doublon
    r2 = await client.post("/admin/blocked-domains", headers=admin_headers, json={
        "domain": "doublon-test.com",
        "reason": "Doublon",
    })
    assert r2.status_code == 409, r2.text


# ---------------------------------------------------------------------------
# Test 8 — Admin supprime un domaine → 204
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_remove_domain(client: AsyncClient, db: AsyncSession, seed_blocked_domains, admin_headers):
    resp = await client.delete("/admin/blocked-domains/yopmail.com", headers=admin_headers)
    assert resp.status_code == 204, resp.text

    # Vérifier qu'il n'est plus listé
    list_resp = await client.get("/admin/blocked-domains", headers=admin_headers)
    domains = [item["domain"] for item in list_resp.json()]
    assert "yopmail.com" not in domains


# ---------------------------------------------------------------------------
# Test 9 — Suppression domaine inexistant → 404
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_remove_nonexistent_domain(client: AsyncClient, db: AsyncSession, admin_headers):
    resp = await client.delete("/admin/blocked-domains/domaine-inexistant.xyz", headers=admin_headers)
    assert resp.status_code == 404, resp.text


# ---------------------------------------------------------------------------
# Test 10 — Non-admin (coach) ne peut pas gérer les domaines bloqués → 403
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_non_admin_cannot_manage_blocked_domains(client: AsyncClient, db: AsyncSession, coach_headers):
    resp = await client.get("/admin/blocked-domains", headers=coach_headers)
    assert resp.status_code == 403, resp.text


# ---------------------------------------------------------------------------
# Test 11 — Test unitaire extract_domain
# ---------------------------------------------------------------------------

def test_extract_domain_helper():
    assert extract_domain("user@gmail.com") == "gmail.com"
    assert extract_domain("USER@YOPMAIL.COM") == "yopmail.com"
    assert extract_domain("  test@example.org  ") == "example.org"
    assert extract_domain("sub@sub.domain.co.uk") == "sub.domain.co.uk"

    # Cas invalides
    import pytest as _pytest
    with _pytest.raises(ValueError):
        extract_domain("invalidemail")
    with _pytest.raises(ValueError):
        extract_domain("noatsign")


# ---------------------------------------------------------------------------
# Test 12 — Inscription réussit après déblocage du domaine
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_after_domain_unblocked(client: AsyncClient, db: AsyncSession, seed_blocked_domains, admin_headers):
    # Vérifier que yopmail.com est bloqué
    resp1 = await client.post("/auth/register", json={
        "first_name": "Dave",
        "last_name": "Yop",
        "email": f"dave_{uuid.uuid4().hex[:6]}@yopmail.com",
        "password": "Password1",
        "confirm_password": "Password1",
        "role": "client",
    })
    assert resp1.status_code == 422, resp1.text

    # Admin débloque yopmail.com
    del_resp = await client.delete("/admin/blocked-domains/yopmail.com", headers=admin_headers)
    assert del_resp.status_code == 204, del_resp.text

    # Maintenant l'inscription doit réussir
    resp2 = await client.post("/auth/register", json={
        "first_name": "Dave",
        "last_name": "Yop",
        "email": f"dave_{uuid.uuid4().hex[:6]}@yopmail.com",
        "password": "Password1",
        "confirm_password": "Password1",
        "role": "client",
    })
    assert resp2.status_code == 201, resp2.text

"""Tests Phase 1 — Forfaits & paiements — B1-27."""

import uuid
from datetime import date, datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

BASE_PROFILE = {"bio": "Coach test", "currency": "EUR", "session_duration_min": 60}

PACKAGE_DATA = {
    "name": "Pack 10 séances",
    "sessions_total": 10,
    "price_cents": 50000,
    "currency": "EUR",
}

PAYMENT_DATA = {
    "amount_cents": 5000,
    "currency": "EUR",
    "payment_method": "card",
}


async def _setup_coach(client, key):
    """Crée le profil coach."""
    await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": key})


async def _get_client_id(db: AsyncSession) -> uuid.UUID:
    """Crée un utilisateur client en base et retourne son id."""
    from app.repositories.user_repository import user_repository
    u = await user_repository.create(
        db,
        first_name="Client",
        last_name="Test",
        email=f"client_{uuid.uuid4().hex[:6]}@test.com",
        role="client",
        password_plain="Password1",
    )
    await db.commit()
    return u.id


# ── Tests forfaits ─────────────────────────────────────────────────────────────

class TestPackages:
    async def test_create_package_ok(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Créer un forfait pour un client."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.post(
            f"/coaches/clients/{client_id}/packages",
            json=PACKAGE_DATA,
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Pack 10 séances"
        assert data["sessions_total"] == 10
        assert data["sessions_remaining"] == 10
        assert data["price_cents"] == 50000
        assert data["status"] == "active"

    async def test_create_package_with_validity(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Créer un forfait avec date de validité."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.post(
            f"/coaches/clients/{client_id}/packages",
            json={**PACKAGE_DATA, "valid_until": "2027-12-31"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["valid_until"] == "2027-12-31"

    async def test_create_package_negative_price(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """❌ Prix négatif → 422."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.post(
            f"/coaches/clients/{client_id}/packages",
            json={**PACKAGE_DATA, "price_cents": -100},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_create_package_zero_sessions(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """❌ sessions_total = 0 → 422."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.post(
            f"/coaches/clients/{client_id}/packages",
            json={**PACKAGE_DATA, "sessions_total": 0},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_list_packages_ok(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Lister les forfaits d'un client."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        await client.post(
            f"/coaches/clients/{client_id}/packages",
            json=PACKAGE_DATA,
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get(
            f"/coaches/clients/{client_id}/packages",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_list_packages_empty(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Aucun forfait → liste vide."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.get(
            f"/coaches/clients/{client_id}/packages",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_client_cannot_create_package(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """❌ Client ne peut pas créer un forfait → 403."""
        client_id = await _get_client_id(db)
        resp = await client.post(
            f"/coaches/clients/{client_id}/packages",
            json=PACKAGE_DATA,
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 403

    async def test_packages_no_auth(self, client: AsyncClient, db: AsyncSession):
        """❌ Sans clé API → 401."""
        client_id = await _get_client_id(db)
        resp = await client.get(f"/coaches/clients/{client_id}/packages")
        assert resp.status_code == 401


# ── Tests paiements ────────────────────────────────────────────────────────────

class TestPayments:
    async def test_record_payment_ok(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Enregistrer un paiement comptant."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.post(
            f"/coaches/clients/{client_id}/payments",
            json=PAYMENT_DATA,
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["amount_cents"] == 5000
        assert data["payment_method"] == "card"
        assert data["status"] == "pending"  # pas de paid_at

    async def test_record_payment_with_date(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Paiement avec date → status 'paid'."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.post(
            f"/coaches/clients/{client_id}/payments",
            json={**PAYMENT_DATA, "paid_at": "2026-02-01T10:00:00Z"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "paid"

    async def test_record_payment_linked_to_package(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Paiement lié à un forfait."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        # Créer un forfait
        pkg_resp = await client.post(
            f"/coaches/clients/{client_id}/packages",
            json=PACKAGE_DATA,
            headers={"X-API-Key": coach_api_key},
        )
        pkg_id = pkg_resp.json()["id"]
        # Paiement lié
        resp = await client.post(
            f"/coaches/clients/{client_id}/payments",
            json={**PAYMENT_DATA, "package_id": pkg_id},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["package_id"] == pkg_id

    async def test_record_payment_invalid_method(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """❌ Méthode de paiement invalide → 422."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.post(
            f"/coaches/clients/{client_id}/payments",
            json={**PAYMENT_DATA, "payment_method": "magic_beans"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_payment_history_ok(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Historique des paiements."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        await client.post(
            f"/coaches/clients/{client_id}/payments",
            json=PAYMENT_DATA,
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get(
            f"/coaches/clients/{client_id}/payments",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    async def test_payment_history_empty(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Historique vide au départ."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.get(
            f"/coaches/clients/{client_id}/payments",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


# ── Tests résumé heures ────────────────────────────────────────────────────────

class TestHoursSummary:
    async def test_hours_no_package(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Résumé sans forfait actif."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        resp = await client.get(
            f"/coaches/clients/{client_id}/hours",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["active_package"] is None
        assert data["sessions_remaining"] == 0
        assert data["sessions_done"] == 0
        assert data["alert_low_sessions"] is False

    async def test_hours_with_package(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Résumé avec forfait actif."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        await client.post(
            f"/coaches/clients/{client_id}/packages",
            json={**PACKAGE_DATA, "sessions_total": 5},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get(
            f"/coaches/clients/{client_id}/hours",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["active_package"] is not None
        assert data["sessions_remaining"] == 5
        assert data["sessions_total_all_time"] == 5

    async def test_hours_alert_low_sessions(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Alerte déclenchée si sessions_remaining <= 2."""
        await _setup_coach(client, coach_api_key)
        client_id = await _get_client_id(db)
        await client.post(
            f"/coaches/clients/{client_id}/packages",
            json={**PACKAGE_DATA, "sessions_total": 2},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get(
            f"/coaches/clients/{client_id}/hours",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["alert_low_sessions"] is True

    async def test_hours_unauthorized(self, client: AsyncClient, db: AsyncSession):
        """❌ Sans clé API → 401."""
        client_id = await _get_client_id(db)
        resp = await client.get(f"/coaches/clients/{client_id}/hours")
        assert resp.status_code == 401

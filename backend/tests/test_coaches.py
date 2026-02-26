"""Tests Phase 1 — Profil coach, clients, salles, forfaits, paiements — B1-28.

Cas passants + cas non passants pour :
  - CRUD profil coach
  - Spécialités, certifications, pricing, disponibilités
  - Politique d'annulation
  - Listing clients
  - Salles (search)
  - Forfaits + paiements + résumé heures
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


COACH_HEADERS = {}
CLIENT_HEADERS = {}

BASE_COACH = {
    "bio": "Coach certifié BPJEPS",
    "currency": "EUR",
    "session_duration_min": 60,
    "discovery_enabled": True,
    "discovery_free": True,
    "booking_horizon_days": 30,
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _create_profile(client: AsyncClient, key: str, data: dict | None = None) -> dict:
    payload = data or BASE_COACH
    resp = await client.post(
        "/coaches/profile",
        json=payload,
        headers={"X-API-Key": key},
    )
    return resp


# ─── CRUD Profil ──────────────────────────────────────────────────────────────

class TestCoachProfile:
    async def test_create_profile_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Créer un profil coach."""
        resp = await _create_profile(client, coach_api_key)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["currency"] == "EUR"
        assert data["session_duration_min"] == 60
        assert data["onboarding_completed"] is False

    async def test_create_profile_duplicate(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Créer un profil deux fois → 409."""
        await _create_profile(client, coach_api_key)
        resp = await _create_profile(client, coach_api_key)
        assert resp.status_code == 409

    async def test_create_profile_client_role_forbidden(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Rôle client ne peut pas créer un profil coach → 403."""
        resp = await _create_profile(client, client_api_key)
        assert resp.status_code == 403

    async def test_get_profile_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ GET /coaches/profile après création."""
        await _create_profile(client, coach_api_key)
        resp = await client.get(
            "/coaches/profile", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 200
        assert "specialties" in resp.json()
        assert "cancellation_policy" in resp.json()

    async def test_get_profile_not_found(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Profil coach inexistant → 404."""
        resp = await client.get(
            "/coaches/profile", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 404

    async def test_update_profile_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ PUT /coaches/profile — mise à jour bio."""
        await _create_profile(client, coach_api_key)
        resp = await client.put(
            "/coaches/profile",
            json={"bio": "Nouveau bio"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["bio"] == "Nouveau bio"

    async def test_update_profile_duration_invalid(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Duration hors limites → 422."""
        await _create_profile(client, coach_api_key)
        resp = await client.put(
            "/coaches/profile",
            json={"session_duration_min": 5},  # < 15
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422


# ─── Spécialités ──────────────────────────────────────────────────────────────

class TestSpecialties:
    async def _setup(self, client, key):
        await _create_profile(client, key)

    async def test_add_specialty_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Ajouter une spécialité valide."""
        await self._setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/profile/specialties",
            json={"specialty": "yoga"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["specialty"] == "yoga"

    async def test_add_specialty_invalid(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Spécialité inconnue → 422."""
        await self._setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/profile/specialties",
            json={"specialty": "bowling"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_delete_specialty_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Supprimer une spécialité."""
        await self._setup(client, coach_api_key)
        add_resp = await client.post(
            "/coaches/profile/specialties",
            json={"specialty": "muscu"},
            headers={"X-API-Key": coach_api_key},
        )
        spec_id = add_resp.json()["id"]
        del_resp = await client.delete(
            f"/coaches/profile/specialties/{spec_id}",
            headers={"X-API-Key": coach_api_key},
        )
        assert del_resp.status_code == 200

    async def test_delete_specialty_not_found(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Supprimer une spécialité inexistante → 404."""
        await self._setup(client, coach_api_key)
        resp = await client.delete(
            f"/coaches/profile/specialties/{uuid.uuid4()}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 404


# ─── Pricing ──────────────────────────────────────────────────────────────────

class TestPricing:
    async def _setup(self, client, key):
        await _create_profile(client, key)

    async def test_create_pricing_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Créer un tarif à la séance."""
        await self._setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/pricing",
            json={"type": "per_session", "name": "Séance unitaire", "price_cents": 5000},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["price_cents"] == 5000

    async def test_create_pricing_invalid_type(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Type de tarif invalide → 422."""
        await self._setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/pricing",
            json={"type": "subscription", "name": "Test", "price_cents": 1000},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_list_pricing_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Lister les tarifs."""
        await self._setup(client, coach_api_key)
        await client.post(
            "/coaches/pricing",
            json={"type": "per_session", "name": "S1", "price_cents": 4500},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get("/coaches/pricing", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_delete_pricing_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Supprimer un tarif."""
        await self._setup(client, coach_api_key)
        add = await client.post(
            "/coaches/pricing",
            json={"type": "per_session", "name": "S2", "price_cents": 3000},
            headers={"X-API-Key": coach_api_key},
        )
        pricing_id = add.json()["id"]
        resp = await client.delete(
            f"/coaches/pricing/{pricing_id}", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 200


# ─── Politique d'annulation ───────────────────────────────────────────────────

class TestCancellationPolicy:
    async def test_set_policy_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Définir la politique d'annulation."""
        await _create_profile(client, coach_api_key)
        resp = await client.put(
            "/coaches/cancellation-policy",
            json={"threshold_hours": 48, "mode": "auto", "noshow_is_due": True},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["threshold_hours"] == 48

    async def test_set_policy_invalid_mode(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Mode invalide → 422."""
        await _create_profile(client, coach_api_key)
        resp = await client.put(
            "/coaches/cancellation-policy",
            json={"mode": "strict"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422


# ─── Clients ──────────────────────────────────────────────────────────────────

class TestClients:
    async def test_list_clients_empty(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Lister les clients — liste vide au départ."""
        await _create_profile(client, coach_api_key)
        resp = await client.get(
            "/coaches/clients", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_update_relation_ok(
        self, client: AsyncClient, coach_api_key: str, client_user
    ):
        """✅ Créer/mettre à jour une relation coach-client."""
        await _create_profile(client, coach_api_key)
        resp = await client.put(
            f"/coaches/clients/{client_user.id}/relation",
            json={"status": "active"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "active"

    async def test_update_note_ok(
        self, client: AsyncClient, coach_api_key: str, client_user
    ):
        """✅ Enregistrer/mettre à jour une note sur un client."""
        await _create_profile(client, coach_api_key)
        resp = await client.put(
            f"/coaches/clients/{client_user.id}/note",
            json={"content": "Client sérieux, objectif perte de poids."},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200


# ─── Salles de sport ──────────────────────────────────────────────────────────

class TestGyms:
    async def test_list_chains_empty(self, client: AsyncClient):
        """✅ Lister les chaînes (vide en test)."""
        resp = await client.get("/gyms/chains")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_search_gyms_empty(self, client: AsyncClient):
        """✅ Recherche de salles (vide en test)."""
        resp = await client.get("/gyms")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total"] == 0

    async def test_get_gym_not_found(self, client: AsyncClient):
        """❌ Salle inexistante → 404."""
        resp = await client.get(f"/gyms/{uuid.uuid4()}")
        assert resp.status_code == 404


# ─── Forfaits & Paiements ─────────────────────────────────────────────────────

class TestPackagesAndPayments:
    async def test_create_package_ok(
        self, client: AsyncClient, coach_api_key: str, client_user
    ):
        """✅ Créer un forfait pour un client."""
        await _create_profile(client, coach_api_key)
        resp = await client.post(
            f"/coaches/clients/{client_user.id}/packages",
            json={
                "name": "Forfait 10 séances",
                "sessions_total": 10,
                "price_cents": 45000,
                "currency": "EUR",
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["sessions_total"] == 10
        assert data["sessions_remaining"] == 10
        assert data["status"] == "active"

    async def test_create_package_invalid_sessions(
        self, client: AsyncClient, coach_api_key: str, client_user
    ):
        """❌ sessions_total = 0 → 422."""
        await _create_profile(client, coach_api_key)
        resp = await client.post(
            f"/coaches/clients/{client_user.id}/packages",
            json={"name": "Bad", "sessions_total": 0, "price_cents": 1000},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_record_payment_ok(
        self, client: AsyncClient, coach_api_key: str, client_user
    ):
        """✅ Enregistrer un paiement manuel."""
        await _create_profile(client, coach_api_key)
        resp = await client.post(
            f"/coaches/clients/{client_user.id}/payments",
            json={
                "amount_cents": 5000,
                "currency": "EUR",
                "payment_method": "cash",
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["amount_cents"] == 5000
        assert resp.json()["status"] == "pending"

    async def test_record_payment_invalid_method(
        self, client: AsyncClient, coach_api_key: str, client_user
    ):
        """❌ Méthode de paiement inconnue → 422."""
        await _create_profile(client, coach_api_key)
        resp = await client.post(
            f"/coaches/clients/{client_user.id}/payments",
            json={"amount_cents": 5000, "payment_method": "bitcoin"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_hours_summary_no_package(
        self, client: AsyncClient, coach_api_key: str, client_user
    ):
        """✅ Résumé heures — aucun forfait actif."""
        await _create_profile(client, coach_api_key)
        resp = await client.get(
            f"/coaches/clients/{client_user.id}/hours",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["sessions_remaining"] == 0
        assert data["active_package"] is None

    async def test_alert_low_sessions(
        self, client: AsyncClient, coach_api_key: str, client_user
    ):
        """✅ Alerte 2 séances restantes détectée."""
        await _create_profile(client, coach_api_key)
        # Créer un forfait de 2 séances
        await client.post(
            f"/coaches/clients/{client_user.id}/packages",
            json={"name": "Mini", "sessions_total": 2, "price_cents": 9000},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get(
            f"/coaches/clients/{client_user.id}/hours",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["alert_low_sessions"] is True

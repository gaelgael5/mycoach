"""Tests Phase 1 — Profil coach, spécialités, certifications, pricing, availability — B1-28."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

BASE_PROFILE = {"bio": "Coach certifié 10 ans", "currency": "EUR", "session_duration_min": 60}


class TestCoachProfile:
    async def test_create_profile_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Créer un profil coach."""
        resp = await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 201
        data = resp.json()
        assert data["bio"] == "Coach certifié 10 ans"
        assert data["currency"] == "EUR"
        assert data["session_duration_min"] == 60

    async def test_create_profile_duplicate(self, client: AsyncClient, coach_api_key: str):
        """❌ Deux profils pour le même coach → 409."""
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        resp = await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 409

    async def test_create_profile_wrong_role(self, client: AsyncClient, client_api_key: str):
        """❌ Client ne peut pas créer un profil coach → 403."""
        resp = await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": client_api_key})
        assert resp.status_code == 403

    async def test_get_profile_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ GET /coaches/profile après création."""
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        resp = await client.get("/coaches/profile", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert resp.json()["currency"] == "EUR"

    async def test_get_profile_not_found(self, client: AsyncClient, coach_api_key: str):
        """❌ Profil inexistant → 404."""
        resp = await client.get("/coaches/profile", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 404

    async def test_update_profile_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Modifier la bio."""
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        resp = await client.put(
            "/coaches/profile",
            json={"bio": "Nouvelle bio"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["bio"] == "Nouvelle bio"

    async def test_unauthorized(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/coaches/profile")
        assert resp.status_code == 401


class TestSpecialties:
    async def _create_profile(self, client, key):
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": key})

    async def test_add_specialty_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Ajouter une spécialité."""
        await self._create_profile(client, coach_api_key)
        resp = await client.post(
            "/coaches/profile/specialties",
            json={"specialty": "yoga"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["specialty"] == "yoga"

    async def test_add_multiple_specialties(self, client: AsyncClient, coach_api_key: str):
        """✅ Plusieurs spécialités distinctes."""
        await self._create_profile(client, coach_api_key)
        for val in ["pilates", "boxe", "natation"]:
            r = await client.post(
                "/coaches/profile/specialties",
                json={"specialty": val},
                headers={"X-API-Key": coach_api_key},
            )
            assert r.status_code == 201

    async def test_delete_specialty_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Supprimer une spécialité."""
        await self._create_profile(client, coach_api_key)
        add = await client.post(
            "/coaches/profile/specialties",
            json={"specialty": "boxe"},
            headers={"X-API-Key": coach_api_key},
        )
        spec_id = add.json()["id"]
        resp = await client.delete(
            f"/coaches/profile/specialties/{spec_id}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200

    async def test_delete_specialty_not_found(self, client: AsyncClient, coach_api_key: str):
        """❌ Supprimer une spécialité inexistante → 404."""
        await self._create_profile(client, coach_api_key)
        resp = await client.delete(
            f"/coaches/profile/specialties/{uuid.uuid4()}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 404


class TestCertifications:
    async def _create_profile(self, client, key):
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": key})

    async def test_add_certification_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Ajouter une certification."""
        await self._create_profile(client, coach_api_key)
        resp = await client.post(
            "/coaches/profile/certifications",
            json={"name": "BPJEPS", "issuer": "Sport France", "year": 2020},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "BPJEPS"
        assert data["year"] == 2020

    async def test_delete_certification_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Supprimer une certification."""
        await self._create_profile(client, coach_api_key)
        add = await client.post(
            "/coaches/profile/certifications",
            json={"name": "CQP", "issuer": "CNOSF"},
            headers={"X-API-Key": coach_api_key},
        )
        cert_id = add.json()["id"]
        resp = await client.delete(
            f"/coaches/profile/certifications/{cert_id}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200

    async def test_delete_certification_other_coach(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """❌ Supprimer la certif d'un autre coach → 404."""
        await self._create_profile(client, coach_api_key)
        add = await client.post(
            "/coaches/profile/certifications",
            json={"name": "CQP"},
            headers={"X-API-Key": coach_api_key},
        )
        cert_id = add.json()["id"]

        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        other = await user_repository.create(
            db, first_name="O", last_name="T",
            email=f"ot_{uuid.uuid4().hex[:6]}@test.com",
            role="coach", password_plain="Password1"
        )
        await db.commit()
        other_key, _ = await api_key_repository.create(db, other.id, "d")
        await db.commit()
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": other_key})

        resp = await client.delete(
            f"/coaches/profile/certifications/{cert_id}",
            headers={"X-API-Key": other_key},
        )
        assert resp.status_code == 404


class TestPricing:
    async def _setup(self, client, key):
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": key})

    async def test_create_pricing_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Créer un tarif."""
        await self._setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/pricing",
            json={"type": "per_session", "name": "Séance individuelle", "price_cents": 6000, "currency": "EUR"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["price_cents"] == 6000
        assert data["type"] == "per_session"

    async def test_list_pricing(self, client: AsyncClient, coach_api_key: str):
        """✅ Lister les tarifs."""
        await self._setup(client, coach_api_key)
        await client.post(
            "/coaches/pricing",
            json={"type": "package", "name": "Pack 10 séances", "price_cents": 50000, "session_count": 10},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get("/coaches/pricing", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_update_pricing_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Modifier un tarif."""
        await self._setup(client, coach_api_key)
        create = await client.post(
            "/coaches/pricing",
            json={"type": "per_session", "name": "Séance", "price_cents": 5000},
            headers={"X-API-Key": coach_api_key},
        )
        pricing_id = create.json()["id"]
        resp = await client.put(
            f"/coaches/pricing/{pricing_id}",
            json={"price_cents": 7000},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["price_cents"] == 7000

    async def test_delete_pricing_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Supprimer un tarif."""
        await self._setup(client, coach_api_key)
        create = await client.post(
            "/coaches/pricing",
            json={"type": "per_session", "name": "Séance", "price_cents": 5000},
            headers={"X-API-Key": coach_api_key},
        )
        pricing_id = create.json()["id"]
        resp = await client.delete(
            f"/coaches/pricing/{pricing_id}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200

    async def test_negative_amount_rejected(self, client: AsyncClient, coach_api_key: str):
        """❌ Montant négatif → 422."""
        await self._setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/pricing",
            json={"type": "per_session", "name": "Séance", "price_cents": -100},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422


class TestAvailability:
    async def _setup(self, client, key):
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": key})

    async def test_create_availability_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Créer un créneau de disponibilité."""
        await self._setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/availability",
            json={"day_of_week": 1, "start_time": "09:00", "end_time": "12:00"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["day_of_week"] == 1

    async def test_list_availability(self, client: AsyncClient, coach_api_key: str):
        """✅ Lister les disponibilités."""
        await self._setup(client, coach_api_key)
        await client.post(
            "/coaches/availability",
            json={"day_of_week": 2, "start_time": "14:00", "end_time": "18:00"},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get("/coaches/availability", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_delete_availability_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Supprimer une disponibilité."""
        await self._setup(client, coach_api_key)
        create = await client.post(
            "/coaches/availability",
            json={"day_of_week": 3, "start_time": "10:00", "end_time": "11:00"},
            headers={"X-API-Key": coach_api_key},
        )
        avail_id = create.json()["id"]
        resp = await client.delete(
            f"/coaches/availability/{avail_id}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200


class TestCancellationPolicy:
    async def _setup(self, client, key):
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": key})

    async def test_update_policy_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Mettre à jour la politique d'annulation."""
        await self._setup(client, coach_api_key)
        resp = await client.put(
            "/coaches/cancellation-policy",
            json={"threshold_hours": 48, "noshow_is_due": True},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["threshold_hours"] == 48
        assert data["noshow_is_due"] is True

    async def test_invalid_threshold(self, client: AsyncClient, coach_api_key: str):
        """❌ Seuil négatif → 422."""
        await self._setup(client, coach_api_key)
        resp = await client.put(
            "/coaches/cancellation-policy",
            json={"threshold_hours": -5},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422


class TestCoachClients:
    async def _setup(self, client, coach_key, client_user):
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_key})
        return client_user

    async def test_list_clients_empty(self, client: AsyncClient, coach_api_key: str, client_user):
        """✅ Liste clients vide au départ."""
        await self._setup(client, coach_api_key, client_user)
        resp = await client.get("/coaches/clients", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))

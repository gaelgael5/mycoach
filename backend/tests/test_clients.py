"""Tests Phase 2 — Profil client, questionnaire, recherche coaches — B2-24."""

import pytest
from httpx import AsyncClient


BASE_CLIENT = {
    "goal": "lose_weight",
    "level": "beginner",
    "weight_unit": "kg",
    "country": "FR",
}


class TestClientProfile:
    async def test_create_profile_ok(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Créer un profil client."""
        resp = await client.post(
            "/clients/profile", json=BASE_CLIENT, headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["goal"] == "lose_weight"
        assert data["onboarding_completed"] is False

    async def test_create_profile_duplicate(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Créer un profil deux fois → 409."""
        await client.post("/clients/profile", json=BASE_CLIENT, headers={"X-API-Key": client_api_key})
        resp = await client.post("/clients/profile", json=BASE_CLIENT, headers={"X-API-Key": client_api_key})
        assert resp.status_code == 409

    async def test_create_profile_wrong_role(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Coach ne peut pas créer un profil client → 403."""
        resp = await client.post(
            "/clients/profile", json=BASE_CLIENT, headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 403

    async def test_get_profile_ok(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ GET /clients/profile après création."""
        await client.post("/clients/profile", json=BASE_CLIENT, headers={"X-API-Key": client_api_key})
        resp = await client.get("/clients/profile", headers={"X-API-Key": client_api_key})
        assert resp.status_code == 200

    async def test_get_profile_not_found(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Profil inexistant → 404."""
        resp = await client.get("/clients/profile", headers={"X-API-Key": client_api_key})
        assert resp.status_code == 404

    async def test_update_profile_ok(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Mettre à jour le niveau."""
        await client.post("/clients/profile", json=BASE_CLIENT, headers={"X-API-Key": client_api_key})
        resp = await client.put(
            "/clients/profile",
            json={"level": "advanced"},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["level"] == "advanced"

    async def test_invalid_goal(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Objectif invalide → 422."""
        resp = await client.post(
            "/clients/profile",
            json={**BASE_CLIENT, "goal": "become_hulk"},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 422


class TestQuestionnaire:
    async def _setup(self, client, key):
        await client.post("/clients/profile", json=BASE_CLIENT, headers={"X-API-Key": key})

    async def test_create_questionnaire_ok(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Créer un questionnaire."""
        await self._setup(client, client_api_key)
        resp = await client.post(
            "/clients/questionnaire",
            json={
                "goal": "muscle_gain",
                "frequency_per_week": 3,
                "equipment": ["haltères", "barre"],
                "target_zones": ["dos", "biceps"],
            },
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["frequency_per_week"] == 3
        assert "haltères" in data["equipment"]

    async def test_upsert_questionnaire(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Créer puis mettre à jour un questionnaire (upsert)."""
        await self._setup(client, client_api_key)
        await client.post(
            "/clients/questionnaire",
            json={"goal": "endurance", "frequency_per_week": 2},
            headers={"X-API-Key": client_api_key},
        )
        resp = await client.put(
            "/clients/questionnaire",
            json={"goal": "well_being", "frequency_per_week": 5},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["goal"] == "well_being"

    async def test_get_questionnaire_not_found(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Questionnaire inexistant → 404."""
        await self._setup(client, client_api_key)
        resp = await client.get("/clients/questionnaire", headers={"X-API-Key": client_api_key})
        assert resp.status_code == 404


class TestCoachSearch:
    async def test_search_coaches_ok(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Recherche de coaches (liste vide si aucun profil public)."""
        resp = await client.get(
            "/clients/coaches/search", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_search_coaches_unauthorized(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/clients/coaches/search")
        assert resp.status_code == 401

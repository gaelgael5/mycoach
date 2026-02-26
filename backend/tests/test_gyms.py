"""Tests Phase 1 — Salles de sport — B1-26."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.models.gym_chain import GymChain
from app.models.gym import Gym


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _seed_chain(db: AsyncSession, name: str = "Test Chain", country: str = "FR") -> GymChain:
    chain = GymChain(
        id=uuid.uuid4(),
        name=name,
        slug=name.lower().replace(" ", "-"),
        country=country,
        active=True,
    )
    db.add(chain)
    await db.flush()
    return chain


async def _seed_gym(
    db: AsyncSession,
    chain: GymChain,
    city: str = "Paris",
    zip_code: str = "75001",
    name: str | None = None,
) -> Gym:
    gym = Gym(
        id=uuid.uuid4(),
        chain_id=chain.id,
        name=name or f"Salle {city}",
        city=city,
        zip_code=zip_code,
        country=chain.country or "FR",
        validated=True,
        open_24h=False,
    )
    db.add(gym)
    await db.flush()
    return gym


# ── Tests chaînes ──────────────────────────────────────────────────────────────

class TestGymChains:
    async def test_list_chains_empty(self, client: AsyncClient):
        """✅ Liste vide sans données."""
        resp = await client.get("/gyms/chains")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_chains_ok(self, client: AsyncClient, db: AsyncSession):
        """✅ Retourne les chaînes en base."""
        await _seed_chain(db, "BasicFit", "FR")
        await _seed_chain(db, "MagicForm", "FR")
        await db.commit()
        resp = await client.get("/gyms/chains")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_list_chains_filter_country(self, client: AsyncClient, db: AsyncSession):
        """✅ Filtrer par pays."""
        await _seed_chain(db, "FrenchChain", "FR")
        await _seed_chain(db, "SpanishChain", "ES")
        await db.commit()
        resp = await client.get("/gyms/chains?country=FR")
        assert resp.status_code == 200
        data = resp.json()
        assert all(c["country"] == "FR" for c in data)
        assert len(data) == 1

    async def test_list_chains_response_fields(self, client: AsyncClient, db: AsyncSession):
        """✅ Vérifie les champs de la réponse."""
        await _seed_chain(db, "FieldTest", "FR")
        await db.commit()
        resp = await client.get("/gyms/chains")
        chain = resp.json()[0]
        assert "id" in chain
        assert "name" in chain
        assert "slug" in chain
        assert "country" in chain
        assert "active" in chain


# ── Tests salles ───────────────────────────────────────────────────────────────

class TestGyms:
    async def test_search_gyms_empty(self, client: AsyncClient):
        """✅ Liste vide sans données."""
        resp = await client.get("/gyms")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_search_gyms_ok(self, client: AsyncClient, db: AsyncSession):
        """✅ Retourne les salles en base."""
        chain = await _seed_chain(db, "MyChain")
        await _seed_gym(db, chain, "Paris")
        await _seed_gym(db, chain, "Lyon")
        await db.commit()
        resp = await client.get("/gyms")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    async def test_search_gyms_filter_city(self, client: AsyncClient, db: AsyncSession):
        """✅ Filtrer par ville."""
        chain = await _seed_chain(db, "CityChain")
        await _seed_gym(db, chain, "Paris")
        await _seed_gym(db, chain, "Lyon")
        await db.commit()
        resp = await client.get("/gyms?city=Paris")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["city"] == "Paris"

    async def test_search_gyms_filter_chain(self, client: AsyncClient, db: AsyncSession):
        """✅ Filtrer par chaîne."""
        chain_a = await _seed_chain(db, "ChainA")
        chain_b = await _seed_chain(db, "ChainB")
        await _seed_gym(db, chain_a, "Paris")
        await _seed_gym(db, chain_b, "Paris")
        await db.commit()
        resp = await client.get(f"/gyms?chain_id={chain_a.id}")
        data = resp.json()
        assert data["total"] == 1
        assert str(data["items"][0]["chain_id"]) == str(chain_a.id)

    async def test_search_gyms_filter_q(self, client: AsyncClient, db: AsyncSession):
        """✅ Recherche libre sur le nom."""
        chain = await _seed_chain(db, "SearchChain")
        await _seed_gym(db, chain, "Paris", name="Salle Force")
        await _seed_gym(db, chain, "Paris", name="Salle Zen")
        await db.commit()
        resp = await client.get("/gyms?q=Force")
        data = resp.json()
        assert data["total"] == 1
        assert "Force" in data["items"][0]["name"]

    async def test_search_gyms_pagination(self, client: AsyncClient, db: AsyncSession):
        """✅ Pagination offset/limit."""
        chain = await _seed_chain(db, "PageChain")
        for i in range(5):
            await _seed_gym(db, chain, f"Ville{i}")
        await db.commit()
        resp = await client.get("/gyms?offset=0&limit=2")
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["offset"] == 0
        assert data["limit"] == 2

    async def test_get_gym_by_id_ok(self, client: AsyncClient, db: AsyncSession):
        """✅ GET /gyms/{id}."""
        chain = await _seed_chain(db, "IdChain")
        gym = await _seed_gym(db, chain, "Marseille")
        await db.commit()
        resp = await client.get(f"/gyms/{gym.id}")
        assert resp.status_code == 200
        assert resp.json()["city"] == "Marseille"

    async def test_get_gym_not_found(self, client: AsyncClient):
        """❌ ID inexistant → 404."""
        resp = await client.get(f"/gyms/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_gyms_no_auth_required(self, client: AsyncClient):
        """✅ Les endpoints gyms sont publics (pas besoin de clé API)."""
        resp = await client.get("/gyms")
        assert resp.status_code == 200

    async def test_gyms_response_fields(self, client: AsyncClient, db: AsyncSession):
        """✅ Vérifie les champs obligatoires de la réponse."""
        chain = await _seed_chain(db, "FieldChain")
        await _seed_gym(db, chain, "Bordeaux")
        await db.commit()
        resp = await client.get("/gyms")
        gym = resp.json()["items"][0]
        for field in ("id", "name", "city", "country", "validated"):
            assert field in gym

"""Tests Phase 7 — Liens réseaux sociaux (social links)."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import user_repository
from app.repositories.api_key_repository import api_key_repository

VALID_PLATFORMS = [
    "instagram", "tiktok", "youtube", "linkedin",
    "x", "facebook", "strava", "website",
]


# ---------------------------------------------------------------------------
# Helper pour créer un second utilisateur coach ou client dans les tests
# ---------------------------------------------------------------------------

async def _make_coach(db: AsyncSession):
    user = await user_repository.create(
        db,
        first_name="Coach2",
        last_name="Test",
        email=f"coach2_{uuid.uuid4().hex[:8]}@test.com",
        role="coach",
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, "test-device")
    await db.commit()
    return user, plain_key


async def _make_client(db: AsyncSession):
    user = await user_repository.create(
        db,
        first_name="Client2",
        last_name="Test",
        email=f"client2_{uuid.uuid4().hex[:8]}@test.com",
        role="client",
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, "test-device")
    await db.commit()
    return user, plain_key


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSocialLinks:

    # 1. GET /users/me/social-links → liste vide initialement
    async def test_list_empty(self, client: AsyncClient, coach_api_key: str):
        """✅ GET /users/me/social-links → liste vide initialement."""
        resp = await client.get("/users/me/social-links/", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert resp.json() == []

    # 2. POST /users/me/social-links → ajout instagram
    async def test_add_instagram(self, client: AsyncClient, coach_api_key: str):
        """✅ POST → ajout d'un lien Instagram."""
        resp = await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "https://instagram.com/monprofil"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "instagram"
        assert data["url"] == "https://instagram.com/monprofil"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

    # 3. POST /users/me/social-links → update instagram (remplace)
    async def test_update_instagram(self, client: AsyncClient, coach_api_key: str):
        """✅ POST deux fois → UPSERT, la deuxième URL remplace la première."""
        await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "https://instagram.com/ancien"},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "https://instagram.com/nouveau"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://instagram.com/nouveau"

        # Vérifier que la liste ne contient qu'un seul lien instagram
        list_resp = await client.get("/users/me/social-links/", headers={"X-API-Key": coach_api_key})
        instagram_links = [l for l in list_resp.json() if l["platform"] == "instagram"]
        assert len(instagram_links) == 1

    # 4. POST /users/me/social-links → 8 plateformes différentes OK
    async def test_add_all_platforms(self, client: AsyncClient, coach_api_key: str):
        """✅ Ajouter les 8 plateformes différentes — toutes acceptées."""
        for platform in VALID_PLATFORMS:
            resp = await client.post(
                "/users/me/social-links/",
                json={"platform": platform, "url": f"https://{platform}.com/monprofil"},
                headers={"X-API-Key": coach_api_key},
            )
            assert resp.status_code == 200, f"Plateforme {platform} refusée"

        # Vérifier que tous les liens sont présents
        list_resp = await client.get("/users/me/social-links/", headers={"X-API-Key": coach_api_key})
        assert len(list_resp.json()) == 8

    # 5. POST /users/me/social-links → plateforme invalide → 422
    async def test_invalid_platform(self, client: AsyncClient, coach_api_key: str):
        """❌ Plateforme inconnue → 422."""
        resp = await client.post(
            "/users/me/social-links/",
            json={"platform": "snapchat", "url": "https://snapchat.com/add/monprofil"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    # 6. POST /users/me/social-links → URL invalide (pas http) → 422
    async def test_invalid_url_no_http(self, client: AsyncClient, coach_api_key: str):
        """❌ URL sans http(s):// → 422."""
        resp = await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "instagram.com/monprofil"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    # 7. URL trop longue → 422
    async def test_invalid_url_too_long(self, client: AsyncClient, coach_api_key: str):
        """❌ URL > 500 chars → 422."""
        long_url = "https://instagram.com/" + "a" * 490
        resp = await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": long_url},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    # 8. DELETE /users/me/social-links/instagram → 204
    async def test_delete_existing_link(self, client: AsyncClient, coach_api_key: str):
        """✅ DELETE → 204 si le lien existe."""
        await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "https://instagram.com/monprofil"},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.delete(
            "/users/me/social-links/instagram",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 204

        # Vérifier que le lien a bien été supprimé
        list_resp = await client.get("/users/me/social-links/", headers={"X-API-Key": coach_api_key})
        assert list_resp.json() == []

    # 9. DELETE /users/me/social-links/instagram → 404 si absent
    async def test_delete_nonexistent_link(self, client: AsyncClient, coach_api_key: str):
        """❌ DELETE lien inexistant → 404."""
        resp = await client.delete(
            "/users/me/social-links/instagram",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 404

    # 10. GET /coaches/{id}/social-links → public, retourne les liens du coach
    async def test_get_coach_public_links(
        self, client: AsyncClient, coach_api_key: str, coach_user
    ):
        """✅ GET /coaches/{id}/social-links → liens publics du coach (sans auth)."""
        # Ajouter des liens pour le coach
        await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "https://instagram.com/coach"},
            headers={"X-API-Key": coach_api_key},
        )
        await client.post(
            "/users/me/social-links/",
            json={"platform": "youtube", "url": "https://youtube.com/coach"},
            headers={"X-API-Key": coach_api_key},
        )

        # Accès sans authentification
        resp = await client.get(f"/coaches/{coach_user.id}/social-links")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        platforms = {item["platform"] for item in data}
        assert "instagram" in platforms
        assert "youtube" in platforms

    # 11. GET /coaches/{id}/social-links → 404 si user pas coach
    async def test_get_coach_links_not_a_coach(
        self, client: AsyncClient, client_user
    ):
        """❌ GET /coaches/{id}/social-links avec un ID de client → 404."""
        resp = await client.get(f"/coaches/{client_user.id}/social-links")
        assert resp.status_code == 404

    # 12. GET /coaches/{id}/social-links → 404 si user n'existe pas
    async def test_get_coach_links_unknown_user(self, client: AsyncClient):
        """❌ GET /coaches/{id}/social-links avec un ID inconnu → 404."""
        fake_id = uuid.uuid4()
        resp = await client.get(f"/coaches/{fake_id}/social-links")
        assert resp.status_code == 404

    # 13. POST sans auth → 401
    async def test_post_without_auth(self, client: AsyncClient):
        """❌ POST sans API key → 401."""
        resp = await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "https://instagram.com/monprofil"},
        )
        assert resp.status_code == 401

    # 14. GET sans auth → 401
    async def test_get_without_auth(self, client: AsyncClient):
        """❌ GET sans API key → 401."""
        resp = await client.get("/users/me/social-links/")
        assert resp.status_code == 401

    # 15. Isolation : liens d'un user n'affectent pas un autre
    async def test_link_isolation(self, client: AsyncClient, coach_api_key: str, db: AsyncSession):
        """✅ Les liens d'un utilisateur sont isolés des autres."""
        # Coach 1 ajoute un lien
        await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "https://instagram.com/coach1"},
            headers={"X-API-Key": coach_api_key},
        )

        # Créer un second coach
        _coach2, key2 = await _make_coach(db)

        # Coach 2 n'a pas de liens
        resp = await client.get("/users/me/social-links/", headers={"X-API-Key": key2})
        assert resp.status_code == 200
        assert resp.json() == []

        # Coach 2 ajoute son propre lien instagram
        await client.post(
            "/users/me/social-links/",
            json={"platform": "instagram", "url": "https://instagram.com/coach2"},
            headers={"X-API-Key": key2},
        )

        # Coach 1 voit toujours son propre lien
        resp1 = await client.get("/users/me/social-links/", headers={"X-API-Key": coach_api_key})
        assert len(resp1.json()) == 1
        assert resp1.json()[0]["url"] == "https://instagram.com/coach1"

        # Coach 2 voit son propre lien
        resp2 = await client.get("/users/me/social-links/", headers={"X-API-Key": key2})
        assert len(resp2.json()) == 1
        assert resp2.json()[0]["url"] == "https://instagram.com/coach2"

    # 16. Client peut aussi gérer ses liens
    async def test_client_can_manage_links(self, client: AsyncClient, client_api_key: str):
        """✅ Un client peut aussi ajouter/supprimer des liens."""
        resp = await client.post(
            "/users/me/social-links/",
            json={"platform": "linkedin", "url": "https://linkedin.com/in/client"},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["platform"] == "linkedin"

        list_resp = await client.get("/users/me/social-links/", headers={"X-API-Key": client_api_key})
        assert len(list_resp.json()) == 1

    # 17. URL avec http:// (non-https) est acceptée
    async def test_http_url_accepted(self, client: AsyncClient, coach_api_key: str):
        """✅ URL commençant par http:// (non-https) est acceptée."""
        resp = await client.post(
            "/users/me/social-links/",
            json={"platform": "website", "url": "http://monsite.com"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["url"] == "http://monsite.com"

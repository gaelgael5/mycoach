"""Tests Phase 7 — Liens réseaux sociaux (social links).

Couvre :
- CRUD basique (GET, POST upsert, PUT by ID, DELETE by ID)
- Lien custom (platform=None, label requis)
- Visibilité (public / coaches_only)
- Max 20 liens
- Isolation entre utilisateurs
- Accès public coach (/coaches/{id}/social-links)
- Cas d'erreurs (401, 404, 422)
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.api_key_repository import api_key_repository
from app.repositories.user_repository import user_repository

VALID_PLATFORMS = [
    "instagram", "tiktok", "youtube", "linkedin",
    "x", "facebook", "strava", "website",
]

BASE = "/users/me/social-links"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_coach(db: AsyncSession):
    """Crée un coach avec une API key — pour les tests d'isolation."""
    user = await user_repository.create(
        db,
        first_name="CoachX",
        last_name="Test",
        email=f"coachx_{uuid.uuid4().hex[:8]}@test.com",
        role="coach",
        password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    plain_key, _ = await api_key_repository.create(db, user.id, "device-x")
    await db.commit()
    return user, plain_key


async def _add_link(client, api_key, platform=None, label=None, url=None, visibility="public", position=0):
    """Helper : POST /users/me/social-links et retourne le JSON."""
    payload = {"url": url or "https://example.com/test", "visibility": visibility, "position": position}
    if platform is not None:
        payload["platform"] = platform
    if label is not None:
        payload["label"] = label
    resp = await client.post(f"{BASE}/", json=payload, headers={"X-API-Key": api_key})
    return resp


# ============================================================================
# Classe de tests
# ============================================================================

@pytest.mark.asyncio
class TestSocialLinksBasic:
    """Tests CRUD de base sur les plateformes standard."""

    async def test_list_empty_initially(self, client: AsyncClient, coach_api_key: str):
        """✅ Liste vide initialement."""
        resp = await client.get(f"{BASE}/", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_add_standard_platform(self, client: AsyncClient, coach_api_key: str):
        """✅ POST lien instagram standard — 200 avec tous les champs."""
        resp = await _add_link(client, coach_api_key, platform="instagram", url="https://instagram.com/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == "instagram"
        assert data["url"] == "https://instagram.com/me"
        assert data["visibility"] == "public"
        assert data["position"] == 0
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_upsert_replaces_existing_platform(self, client: AsyncClient, coach_api_key: str):
        """✅ Poster deux fois la même plateforme → UPSERT, URL remplacée."""
        await _add_link(client, coach_api_key, platform="instagram", url="https://instagram.com/ancien")
        resp = await _add_link(client, coach_api_key, platform="instagram", url="https://instagram.com/nouveau")
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://instagram.com/nouveau"

        # Une seule entrée instagram
        list_resp = await client.get(f"{BASE}/", headers={"X-API-Key": coach_api_key})
        instagram = [l for l in list_resp.json() if l["platform"] == "instagram"]
        assert len(instagram) == 1

    async def test_add_all_valid_platforms(self, client: AsyncClient, coach_api_key: str):
        """✅ Les 8 plateformes standard sont toutes acceptées."""
        for p in VALID_PLATFORMS:
            resp = await _add_link(client, coach_api_key, platform=p, url=f"https://{p}.com/me")
            assert resp.status_code == 200, f"Plateforme '{p}' refusée"

        list_resp = await client.get(f"{BASE}/", headers={"X-API-Key": coach_api_key})
        assert len(list_resp.json()) == 8

    async def test_delete_by_id(self, client: AsyncClient, coach_api_key: str):
        """✅ DELETE /{link_id} → 204 + lien supprimé."""
        add_resp = await _add_link(client, coach_api_key, platform="instagram", url="https://instagram.com/me")
        link_id = add_resp.json()["id"]

        del_resp = await client.delete(f"{BASE}/{link_id}", headers={"X-API-Key": coach_api_key})
        assert del_resp.status_code == 204

        list_resp = await client.get(f"{BASE}/", headers={"X-API-Key": coach_api_key})
        assert list_resp.json() == []

    async def test_delete_nonexistent_link(self, client: AsyncClient, coach_api_key: str):
        """❌ DELETE ID inexistant → 404."""
        fake_id = uuid.uuid4()
        resp = await client.delete(f"{BASE}/{fake_id}", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 404

    async def test_put_update_url_and_visibility(self, client: AsyncClient, coach_api_key: str):
        """✅ PUT /{link_id} → mise à jour url + visibility."""
        add_resp = await _add_link(client, coach_api_key, platform="instagram", url="https://instagram.com/me")
        link_id = add_resp.json()["id"]

        put_resp = await client.put(
            f"{BASE}/{link_id}",
            json={"url": "https://instagram.com/updated", "visibility": "coaches_only"},
            headers={"X-API-Key": coach_api_key},
        )
        assert put_resp.status_code == 200
        data = put_resp.json()
        assert data["url"] == "https://instagram.com/updated"
        assert data["visibility"] == "coaches_only"
        assert data["platform"] == "instagram"

    async def test_put_another_user_link_is_404(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """❌ PUT lien appartenant à un autre user → 404."""
        _, key2 = await _make_coach(db)
        add_resp = await _add_link(client, key2, platform="instagram", url="https://instagram.com/other")
        link_id = add_resp.json()["id"]

        # Coach 1 essaie de modifier le lien du Coach 2
        resp = await client.put(
            f"{BASE}/{link_id}",
            json={"url": "https://hacked.com"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestSocialLinksCustom:
    """Tests spécifiques aux liens personnalisés (platform=None)."""

    async def test_add_custom_link_with_label(self, client: AsyncClient, coach_api_key: str):
        """✅ Lien custom avec label → 200."""
        resp = await _add_link(
            client, coach_api_key,
            label="Mon portfolio", url="https://monportfolio.fr"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] is None
        assert data["label"] == "Mon portfolio"
        assert data["url"] == "https://monportfolio.fr"

    async def test_add_multiple_custom_links(self, client: AsyncClient, coach_api_key: str):
        """✅ Plusieurs liens custom (platform=None) autorisés."""
        await _add_link(client, coach_api_key, label="Portfolio", url="https://portfolio.fr")
        await _add_link(client, coach_api_key, label="Blog", url="https://blog.fr")
        await _add_link(client, coach_api_key, label="Boutique", url="https://boutique.fr")

        list_resp = await client.get(f"{BASE}/", headers={"X-API-Key": coach_api_key})
        custom = [l for l in list_resp.json() if l["platform"] is None]
        assert len(custom) == 3

    async def test_custom_without_label_is_422(self, client: AsyncClient, coach_api_key: str):
        """❌ Lien custom sans label → 422."""
        resp = await client.post(
            f"{BASE}/",
            json={"url": "https://quelquepart.fr"},  # platform=None, pas de label
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_max_20_links_enforced(self, client: AsyncClient, coach_api_key: str):
        """❌ 21ème lien custom → 422 (max 20 atteint)."""
        # On remplit avec 20 liens custom (pas de limite sur custom standard distinct)
        for i in range(20):
            resp = await _add_link(
                client, coach_api_key,
                label=f"Lien custom {i}", url=f"https://example{i}.com"
            )
            assert resp.status_code == 200, f"Lien {i+1}/20 refusé"

        # Le 21ème doit être refusé
        resp = await _add_link(
            client, coach_api_key,
            label="Un lien de trop", url="https://tropplein.com"
        )
        assert resp.status_code == 422
        assert "20" in resp.json()["detail"]


@pytest.mark.asyncio
class TestSocialLinksVisibility:
    """Tests de la visibilité des liens."""

    async def test_visibility_default_is_public(self, client: AsyncClient, coach_api_key: str):
        """✅ Visibilité par défaut = public."""
        resp = await _add_link(client, coach_api_key, platform="instagram", url="https://instagram.com/me")
        assert resp.json()["visibility"] == "public"

    async def test_add_coaches_only_link(self, client: AsyncClient, coach_api_key: str):
        """✅ Lien avec visibility=coaches_only → stocké et retourné pour le propriétaire."""
        resp = await _add_link(
            client, coach_api_key, platform="linkedin",
            url="https://linkedin.com/in/me", visibility="coaches_only"
        )
        assert resp.status_code == 200
        assert resp.json()["visibility"] == "coaches_only"

    async def test_coach_public_endpoint_hides_coaches_only(
        self, client: AsyncClient, coach_api_key: str, coach_user
    ):
        """✅ GET /coaches/{id}/social-links → ne retourne PAS les liens coaches_only."""
        # Lien public
        await _add_link(client, coach_api_key, platform="instagram", url="https://instagram.com/me")
        # Lien coaches_only
        await _add_link(
            client, coach_api_key, platform="linkedin",
            url="https://linkedin.com/in/me", visibility="coaches_only"
        )

        # Endpoint public (sans auth)
        resp = await client.get(f"/coaches/{coach_user.id}/social-links")
        assert resp.status_code == 200
        data = resp.json()
        platforms = {l["platform"] for l in data}
        assert "instagram" in platforms        # public → visible
        assert "linkedin" not in platforms    # coaches_only → masqué

    async def test_invalid_visibility_is_422(self, client: AsyncClient, coach_api_key: str):
        """❌ Visibilité invalide → 422."""
        resp = await client.post(
            f"{BASE}/",
            json={"platform": "instagram", "url": "https://instagram.com/me", "visibility": "private"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestSocialLinksValidation:
    """Tests de validation des entrées."""

    async def test_invalid_platform_name(self, client: AsyncClient, coach_api_key: str):
        """❌ Plateforme non reconnue → 422."""
        resp = await _add_link(client, coach_api_key, platform="snapchat", url="https://snapchat.com/add/me")
        assert resp.status_code == 422

    async def test_url_without_scheme_is_422(self, client: AsyncClient, coach_api_key: str):
        """❌ URL sans http(s):// → 422."""
        resp = await client.post(
            f"{BASE}/",
            json={"platform": "instagram", "url": "instagram.com/me"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_url_too_long_is_422(self, client: AsyncClient, coach_api_key: str):
        """❌ URL > 500 chars → 422."""
        long_url = "https://example.com/" + "a" * 490
        resp = await client.post(
            f"{BASE}/",
            json={"platform": "instagram", "url": long_url},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_http_url_is_accepted(self, client: AsyncClient, coach_api_key: str):
        """✅ URL commençant par http:// (non-https) est acceptée."""
        resp = await _add_link(client, coach_api_key, platform="website", url="http://monsite.fr")
        assert resp.status_code == 200

    async def test_no_auth_get_is_401(self, client: AsyncClient):
        """❌ GET sans API key → 401."""
        resp = await client.get(f"{BASE}/")
        assert resp.status_code == 401

    async def test_no_auth_post_is_401(self, client: AsyncClient):
        """❌ POST sans API key → 401."""
        resp = await client.post(
            f"{BASE}/",
            json={"platform": "instagram", "url": "https://instagram.com/me"},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestSocialLinksIsolation:
    """Tests d'isolation entre utilisateurs."""

    async def test_coach_and_client_links_are_isolated(
        self, client: AsyncClient, coach_api_key: str, client_api_key: str
    ):
        """✅ Client peut gérer ses propres liens, indépendants du coach."""
        await _add_link(client, coach_api_key, platform="instagram", url="https://instagram.com/coach")
        await _add_link(client, client_api_key, platform="instagram", url="https://instagram.com/client")

        coach_links = (await client.get(f"{BASE}/", headers={"X-API-Key": coach_api_key})).json()
        client_links = (await client.get(f"{BASE}/", headers={"X-API-Key": client_api_key})).json()

        assert coach_links[0]["url"] == "https://instagram.com/coach"
        assert client_links[0]["url"] == "https://instagram.com/client"

    async def test_two_coaches_links_are_isolated(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Deux coachs ont des liens indépendants."""
        _, key2 = await _make_coach(db)

        await _add_link(client, coach_api_key, platform="youtube", url="https://youtube.com/coach1")
        await _add_link(client, key2, platform="youtube", url="https://youtube.com/coach2")

        links1 = (await client.get(f"{BASE}/", headers={"X-API-Key": coach_api_key})).json()
        links2 = (await client.get(f"{BASE}/", headers={"X-API-Key": key2})).json()

        assert links1[0]["url"] == "https://youtube.com/coach1"
        assert links2[0]["url"] == "https://youtube.com/coach2"

    async def test_coach_public_endpoint_404_for_client(
        self, client: AsyncClient, client_user
    ):
        """❌ /coaches/{id} avec ID d'un client → 404."""
        resp = await client.get(f"/coaches/{client_user.id}/social-links")
        assert resp.status_code == 404

    async def test_coach_public_endpoint_404_unknown_id(self, client: AsyncClient):
        """❌ /coaches/{id} avec ID inconnu → 404."""
        resp = await client.get(f"/coaches/{uuid.uuid4()}/social-links")
        assert resp.status_code == 404

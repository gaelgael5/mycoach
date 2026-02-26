"""Tests Phase 1 — Templates d'annulation — B1-35."""

import uuid
import pytest
from httpx import AsyncClient

BASE_PROFILE = {"bio": "Coach test", "currency": "EUR", "session_duration_min": 60}

TEMPLATE_MALADIE = {
    "title": "Maladie",
    "body": "Bonjour {prénom}, je dois annuler votre séance du {date} à {heure} car je suis malade.",
}
TEMPLATE_URGENT = {
    "title": "Urgence",
    "body": "Bonjour {prénom}, séance du {date} annulée pour urgence — {coach}.",
}


async def _setup(client, key):
    """Créer le profil coach (déclenche la création du template par défaut)."""
    await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": key})


class TestTemplateCRUD:
    async def test_list_templates_has_default(self, client: AsyncClient, coach_api_key: str):
        """✅ Un template par défaut ('Maladie') est créé automatiquement avec le profil."""
        await _setup(client, coach_api_key)
        resp = await client.get("/coaches/cancellation-templates", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["title"] == "Maladie"

    async def test_create_template_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Créer un template."""
        await _setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/cancellation-templates",
            json=TEMPLATE_URGENT,
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Urgence"
        assert "{prénom}" in data["body"]

    async def test_max_5_templates(self, client: AsyncClient, coach_api_key: str):
        """❌ Plus de 5 templates → 422 (ou 409)."""
        await _setup(client, coach_api_key)
        # Ajouter 4 templates (1 par défaut + 4 = 5 total)
        for i in range(4):
            r = await client.post(
                "/coaches/cancellation-templates",
                json={"title": f"Template {i}", "body": f"Annulation numéro {i}"},
                headers={"X-API-Key": coach_api_key},
            )
            assert r.status_code == 201
        # Le 6e doit échouer
        resp = await client.post(
            "/coaches/cancellation-templates",
            json={"title": "De trop", "body": "Corps"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code in (409, 422)

    async def test_update_template_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Modifier un template."""
        await _setup(client, coach_api_key)
        create = await client.post(
            "/coaches/cancellation-templates",
            json=TEMPLATE_URGENT,
            headers={"X-API-Key": coach_api_key},
        )
        tmpl_id = create.json()["id"]
        resp = await client.put(
            f"/coaches/cancellation-templates/{tmpl_id}",
            json={"title": "Urgence familiale"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Urgence familiale"

    async def test_delete_template_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Supprimer un template non-unique."""
        await _setup(client, coach_api_key)
        # Créer un 2e template (pour pouvoir supprimer le 1er default)
        await client.post(
            "/coaches/cancellation-templates",
            json=TEMPLATE_URGENT,
            headers={"X-API-Key": coach_api_key},
        )
        # Lister pour avoir les IDs
        listing = await client.get(
            "/coaches/cancellation-templates",
            headers={"X-API-Key": coach_api_key},
        )
        tmpl_id = listing.json()[1]["id"]  # le 2e (URGENT)
        resp = await client.delete(
            f"/coaches/cancellation-templates/{tmpl_id}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200

    async def test_delete_last_template_forbidden(self, client: AsyncClient, coach_api_key: str):
        """❌ Supprimer le dernier template restant → 422."""
        await _setup(client, coach_api_key)
        listing = await client.get(
            "/coaches/cancellation-templates",
            headers={"X-API-Key": coach_api_key},
        )
        only_id = listing.json()[0]["id"]
        resp = await client.delete(
            f"/coaches/cancellation-templates/{only_id}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_delete_other_coach_template(
        self, client: AsyncClient, coach_api_key: str, db
    ):
        """❌ Supprimer le template d'un autre coach → 404."""
        await _setup(client, coach_api_key)
        listing = await client.get(
            "/coaches/cancellation-templates",
            headers={"X-API-Key": coach_api_key},
        )
        tmpl_id = listing.json()[0]["id"]

        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        other = await user_repository.create(
            db, first_name="X", last_name="Y",
            email=f"xy_{uuid.uuid4().hex[:6]}@test.com",
            role="coach", password_plain="Password1",
        )
        await db.commit()
        other_key, _ = await api_key_repository.create(db, other.id, "d")
        await db.commit()
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": other_key})

        resp = await client.delete(
            f"/coaches/cancellation-templates/{tmpl_id}",
            headers={"X-API-Key": other_key},
        )
        assert resp.status_code == 404

    async def test_unauthorized(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/coaches/cancellation-templates")
        assert resp.status_code == 401


class TestTemplatePreview:
    async def test_preview_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Prévisualiser un template avec des données fictives."""
        await _setup(client, coach_api_key)
        listing = await client.get(
            "/coaches/cancellation-templates",
            headers={"X-API-Key": coach_api_key},
        )
        tmpl_id = listing.json()[0]["id"]
        resp = await client.post(
            f"/coaches/cancellation-templates/{tmpl_id}/preview",
            json={
                "client_first_name": "Alice",
                "session_date": "15/03/2026",
                "session_time": "10:00",
                "coach_name": "Jean",
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        resolved = resp.json()["resolved_body"]
        assert "Alice" in resolved

    async def test_preview_not_found(self, client: AsyncClient, coach_api_key: str):
        """❌ Preview template inexistant → 404."""
        await _setup(client, coach_api_key)
        resp = await client.post(
            f"/coaches/cancellation-templates/{uuid.uuid4()}/preview",
            json={
                "client_first_name": "Bob",
                "session_date": "15/03/2026",
                "session_time": "10:00",
                "coach_name": "Jean",
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 404


class TestTemplateReorder:
    async def test_reorder_ok(self, client: AsyncClient, coach_api_key: str):
        """✅ Réordonner les templates."""
        await _setup(client, coach_api_key)
        # Créer un 2e template
        await client.post(
            "/coaches/cancellation-templates",
            json=TEMPLATE_URGENT,
            headers={"X-API-Key": coach_api_key},
        )
        listing = await client.get(
            "/coaches/cancellation-templates",
            headers={"X-API-Key": coach_api_key},
        )
        items = listing.json()
        ids = [t["id"] for t in items]
        # Inverser l'ordre : items[0] → position 2, items[1] → position 1
        reorder_items = [
            {"id": ids[0], "position": 2},
            {"id": ids[1], "position": 1},
        ]
        resp = await client.post(
            "/coaches/cancellation-templates/reorder",
            json={"items": reorder_items},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        reordered = resp.json()
        # Après reorder, le 2e template (position 1) doit être en premier
        assert reordered[0]["id"] == ids[1]

    async def test_reorder_wrong_count(self, client: AsyncClient, coach_api_key: str):
        """❌ Réordonner avec des IDs inconnus → 422."""
        await _setup(client, coach_api_key)
        resp = await client.post(
            "/coaches/cancellation-templates/reorder",
            json={"items": [{"id": str(uuid.uuid4()), "position": 1}]},  # ID inconnu
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

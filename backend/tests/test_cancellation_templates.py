"""Tests Phase 1 — Templates de messages d'annulation — B1-35.

Cas passants + cas non passants :
  - Liste vide → seed auto du template Maladie
  - CRUD complet
  - Refus au-delà de 5 templates
  - Refus suppression du dernier template
  - Preview résolution des variables
  - Reorder
"""

import uuid

import pytest
from httpx import AsyncClient


BASE_COACH = {
    "bio": "Coach test",
    "currency": "EUR",
    "session_duration_min": 60,
}


async def _create_profile(client: AsyncClient, key: str) -> None:
    await client.post(
        "/coaches/profile", json=BASE_COACH, headers={"X-API-Key": key}
    )


async def _list_templates(client: AsyncClient, key: str) -> list:
    resp = await client.get(
        "/coaches/cancellation-templates", headers={"X-API-Key": key}
    )
    return resp.json()


class TestCancellationTemplates:

    async def test_list_auto_seed(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Après création de profil, le template 'Maladie' est présent."""
        await _create_profile(client, coach_api_key)
        templates = await _list_templates(client, coach_api_key)
        assert len(templates) == 1
        assert templates[0]["is_default"] is True
        assert templates[0]["title"] == "Maladie"
        assert templates[0]["position"] == 1

    async def test_list_contains_variables(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Le template par défaut contient les variables {prénom}, {date}, etc."""
        await _create_profile(client, coach_api_key)
        templates = await _list_templates(client, coach_api_key)
        vars_used = templates[0]["variables_used"]
        assert "{prénom}" in vars_used
        assert "{coach}" in vars_used

    async def test_create_template_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Créer un nouveau template."""
        await _create_profile(client, coach_api_key)
        resp = await client.post(
            "/coaches/cancellation-templates",
            json={"title": "Urgence pro", "body": "Bonjour {prénom}, séance du {date} annulée."},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Urgence pro"
        assert "{prénom}" in data["variables_used"]
        assert "{date}" in data["variables_used"]

    async def test_create_template_invalid_variable(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Variable inconnue dans body → 422."""
        await _create_profile(client, coach_api_key)
        resp = await client.post(
            "/coaches/cancellation-templates",
            json={"title": "Test", "body": "Bonjour {nom}, votre séance est annulée."},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_create_max_5_templates(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Créer un 6e template → 422."""
        await _create_profile(client, coach_api_key)
        for i in range(4):  # 4 supplémentaires (1 par défaut + 4 = 5 total)
            resp = await client.post(
                "/coaches/cancellation-templates",
                json={"title": f"T{i}", "body": f"Bonjour {'{prénom}'}, séance du {'{date}'} annulée par urgence {i}."},
                headers={"X-API-Key": coach_api_key},
            )
            assert resp.status_code == 201
        # 6e tentative
        resp = await client.post(
            "/coaches/cancellation-templates",
            json={"title": "T6", "body": "Trop de templates {prénom}."},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_update_template_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Modifier le titre d'un template."""
        await _create_profile(client, coach_api_key)
        templates = await _list_templates(client, coach_api_key)
        tid = templates[0]["id"]
        resp = await client.put(
            f"/coaches/cancellation-templates/{tid}",
            json={"title": "Maladie grave"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Maladie grave"

    async def test_update_template_not_found(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Modifier un template inexistant → 404."""
        await _create_profile(client, coach_api_key)
        resp = await client.put(
            f"/coaches/cancellation-templates/{uuid.uuid4()}",
            json={"title": "Fantôme"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 404

    async def test_delete_last_template_refused(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Supprimer le dernier template → 422."""
        await _create_profile(client, coach_api_key)
        templates = await _list_templates(client, coach_api_key)
        tid = templates[0]["id"]
        resp = await client.delete(
            f"/coaches/cancellation-templates/{tid}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_delete_template_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Supprimer un template (quand il en reste un autre)."""
        await _create_profile(client, coach_api_key)
        # Ajouter un 2e template
        await client.post(
            "/coaches/cancellation-templates",
            json={"title": "Vacances", "body": "Bonjour {prénom}, je suis en vacances le {date}."},
            headers={"X-API-Key": coach_api_key},
        )
        templates = await _list_templates(client, coach_api_key)
        # Supprimer le 2e
        non_default = next(t for t in templates if not t["is_default"])
        resp = await client.delete(
            f"/coaches/cancellation-templates/{non_default['id']}",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        # Il reste 1 template
        remaining = await _list_templates(client, coach_api_key)
        assert len(remaining) == 1

    async def test_preview_template(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Preview — variables résolues correctement."""
        await _create_profile(client, coach_api_key)
        templates = await _list_templates(client, coach_api_key)
        tid = templates[0]["id"]
        resp = await client.post(
            f"/coaches/cancellation-templates/{tid}/preview",
            json={
                "client_first_name": "Alice",
                "session_date": "26/02/2026",
                "session_time": "10:00",
                "coach_name": "Bob",
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        resolved = resp.json()["resolved_body"]
        assert "Alice" in resolved
        assert "26/02/2026" in resolved
        assert "10:00" in resolved
        assert "Bob" in resolved
        assert "{prénom}" not in resolved
        assert "{date}" not in resolved

    async def test_preview_not_found(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Preview d'un template inexistant → 404."""
        await _create_profile(client, coach_api_key)
        resp = await client.post(
            f"/coaches/cancellation-templates/{uuid.uuid4()}/preview",
            json={
                "client_first_name": "Alice",
                "session_date": "01/01/2026",
                "session_time": "09:00",
                "coach_name": "Coach",
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 404

    async def test_reorder_templates(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Réordonner 2 templates."""
        await _create_profile(client, coach_api_key)
        # Ajouter un 2e template
        await client.post(
            "/coaches/cancellation-templates",
            json={"title": "T2", "body": "Bonjour {prénom}, reportons le {date}."},
            headers={"X-API-Key": coach_api_key},
        )
        templates = await _list_templates(client, coach_api_key)
        id1, id2 = templates[0]["id"], templates[1]["id"]
        # Inverser les positions
        resp = await client.post(
            "/coaches/cancellation-templates/reorder",
            json={"items": [{"id": id1, "position": 2}, {"id": id2, "position": 1}]},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200

    async def test_reorder_duplicate_position_rejected(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Positions dupliquées dans reorder → 422."""
        await _create_profile(client, coach_api_key)
        await client.post(
            "/coaches/cancellation-templates",
            json={"title": "T2", "body": "Bonjour {prénom}, reportons le {date}."},
            headers={"X-API-Key": coach_api_key},
        )
        templates = await _list_templates(client, coach_api_key)
        id1, id2 = templates[0]["id"], templates[1]["id"]
        resp = await client.post(
            "/coaches/cancellation-templates/reorder",
            json={"items": [{"id": id1, "position": 1}, {"id": id2, "position": 1}]},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

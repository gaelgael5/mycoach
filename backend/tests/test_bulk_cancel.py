"""Tests Phase 2 — Bulk cancel — B2-35."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

BASE_PROFILE = {"bio": "Coach test", "currency": "EUR", "session_duration_min": 60}


def _slot(hours: int = 72) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


async def _create_bookings(client, coach_key, client_key, coach_user, n=2):
    """Crée n réservations confirmées. Retourne leurs IDs."""
    await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_key})
    ids = []
    for i in range(n):
        r = await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _slot(72 + i * 24)},
            headers={"X-API-Key": client_key},
        )
        booking_id = r.json()["id"]
        await client.post(f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_key})
        ids.append(booking_id)
    return ids


class TestBulkCancel:
    async def test_bulk_cancel_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Annuler plusieurs séances en une fois."""
        ids = await _create_bookings(client, coach_api_key, client_api_key, coach_user, n=2)
        resp = await client.post(
            "/coaches/bookings/bulk-cancel",
            json={"booking_ids": ids, "send_sms": False},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["cancelled_count"] == 2
        assert data["sms_sent_count"] == 0

    async def test_bulk_cancel_single(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Annuler une seule séance via bulk."""
        ids = await _create_bookings(client, coach_api_key, client_api_key, coach_user, n=1)
        resp = await client.post(
            "/coaches/bookings/bulk-cancel",
            json={"booking_ids": ids, "send_sms": False},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["cancelled_count"] == 1

    async def test_bulk_cancel_empty_list(
        self,
        client: AsyncClient,
        coach_api_key: str,
    ):
        """✅ Liste vide → 0 annulations."""
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        resp = await client.post(
            "/coaches/bookings/bulk-cancel",
            json={"booking_ids": [], "send_sms": False},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["cancelled_count"] == 0

    async def test_bulk_cancel_other_coach_booking(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
        db: AsyncSession,
    ):
        """❌ Annuler la séance d'un autre coach → 403."""
        ids = await _create_bookings(client, coach_api_key, client_api_key, coach_user, n=1)

        # Créer un autre coach
        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        other = await user_repository.create(
            db, first_name="Pirate", last_name="Coach",
            email=f"pirate_{uuid.uuid4().hex[:6]}@test.com",
            role="coach", password_plain="Password1",
        )
        await db.commit()
        other_key, _ = await api_key_repository.create(db, other.id, "d")
        await db.commit()
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": other_key})

        resp = await client.post(
            "/coaches/bookings/bulk-cancel",
            json={"booking_ids": ids, "send_sms": False},
            headers={"X-API-Key": other_key},
        )
        assert resp.status_code == 403

    async def test_bulk_cancel_nonexistent_booking(
        self,
        client: AsyncClient,
        coach_api_key: str,
    ):
        """❌ ID inconnu → 403 (booking introuvable = accès refusé)."""
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        resp = await client.post(
            "/coaches/bookings/bulk-cancel",
            json={"booking_ids": [str(uuid.uuid4())], "send_sms": False},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 403

    async def test_bulk_cancel_with_template(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Bulk cancel avec template_id fourni (SMS non envoyé en test = ConsoleSmsProvider)."""
        ids = await _create_bookings(client, coach_api_key, client_api_key, coach_user, n=1)

        # Récupérer le template par défaut
        tmpl_resp = await client.get(
            "/coaches/cancellation-templates",
            headers={"X-API-Key": coach_api_key},
        )
        tmpl_id = tmpl_resp.json()[0]["id"]

        resp = await client.post(
            "/coaches/bookings/bulk-cancel",
            json={"booking_ids": ids, "send_sms": True, "template_id": tmpl_id},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["cancelled_count"] == 1
        # SMS non envoyé car client sans numéro de téléphone (expected)
        assert data["sms_sent_count"] == 0

    async def test_bulk_cancel_unauthorized(self, client: AsyncClient, client_api_key: str):
        """❌ Client ne peut pas faire un bulk cancel → 403."""
        resp = await client.post(
            "/coaches/bookings/bulk-cancel",
            json={"booking_ids": [], "send_sms": False},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 403

    async def test_bulk_cancel_no_auth(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.post(
            "/coaches/bookings/bulk-cancel",
            json={"booking_ids": [], "send_sms": False},
        )
        assert resp.status_code == 401


class TestSmsLogs:
    async def test_sms_logs_empty(self, client: AsyncClient, coach_api_key: str):
        """✅ Logs SMS vides au départ."""
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        resp = await client.get("/coaches/sms/logs", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_sms_logs_unauthorized(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/coaches/sms/logs")
        assert resp.status_code == 401

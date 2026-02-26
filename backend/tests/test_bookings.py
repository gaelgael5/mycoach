"""Tests Phase 2 — Réservations, machine d'état — B2-25."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import booking_repository, coach_repository

BASE_COACH = {"bio": "Coach test", "currency": "EUR", "session_duration_min": 60}


def _future_slot(hours: int = 72) -> str:
    """Slot UTC dans N heures."""
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _past_slot(hours: int = 2) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


async def _create_coach_profile(client, key):
    await client.post("/coaches/profile", json=BASE_COACH, headers={"X-API-Key": key})


class TestCreateBooking:
    async def test_create_booking_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Créer une réservation."""
        await _create_coach_profile(client, coach_api_key)
        resp = await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _future_slot()},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending_coach_validation"
        assert data["coach_id"] == str(coach_user.id)

    async def test_create_booking_slot_full(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """❌ Créneau complet (max 1 slot par défaut) → 409."""
        await _create_coach_profile(client, coach_api_key)
        slot = _future_slot(48)
        payload = {"coach_id": str(coach_user.id), "scheduled_at": slot}
        # 1ère réservation — OK
        r1 = await client.post("/bookings", json=payload, headers={"X-API-Key": client_api_key})
        assert r1.status_code == 201
        # 2e réservation sur le même créneau → 409
        r2 = await client.post("/bookings", json=payload, headers={"X-API-Key": client_api_key})
        assert r2.status_code == 409

    async def test_create_booking_unauthorized(self, client: AsyncClient, coach_api_key: str, coach_user):
        """❌ Sans clé API → 401."""
        resp = await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _future_slot()},
        )
        assert resp.status_code == 401


class TestBookingStateTransitions:
    async def _setup_booking(self, client, coach_api_key, coach_user, client_api_key):
        """Crée un profil coach + une réservation en pending."""
        await _create_coach_profile(client, coach_api_key)
        resp = await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _future_slot()},
            headers={"X-API-Key": client_api_key},
        )
        return resp.json()["id"]

    async def test_confirm_booking_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Coach confirme une réservation."""
        booking_id = await self._setup_booking(client, coach_api_key, coach_user, client_api_key)
        resp = await client.post(
            f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"

    async def test_confirm_already_confirmed(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """❌ Confirmer deux fois → 422."""
        booking_id = await self._setup_booking(client, coach_api_key, coach_user, client_api_key)
        await client.post(f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_api_key})
        resp = await client.post(f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 422

    async def test_reject_booking_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Coach rejette une réservation."""
        booking_id = await self._setup_booking(client, coach_api_key, coach_user, client_api_key)
        resp = await client.post(
            f"/bookings/{booking_id}/reject",
            json={"reason": "Créneau non disponible"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    async def test_client_cancel_before_threshold(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Client annule avant le délai → cancelled_by_client (sans pénalité)."""
        await _create_coach_profile(client, coach_api_key)
        # Séance dans 72h (bien au-delà du seuil de 24h)
        resp = await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _future_slot(72)},
            headers={"X-API-Key": client_api_key},
        )
        booking_id = resp.json()["id"]
        # Confirmer
        await client.post(f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_api_key})
        # Annuler
        resp = await client.delete(
            f"/bookings/{booking_id}",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled_by_client"

    async def test_client_cancel_after_threshold(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
        db: AsyncSession,
    ):
        """✅ Client annule après le délai → cancelled_late_by_client."""
        await _create_coach_profile(client, coach_api_key)
        # Séance dans 2h (< seuil de 24h)
        resp = await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _future_slot(2)},
            headers={"X-API-Key": client_api_key},
        )
        booking_id = resp.json()["id"]
        await client.post(f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_api_key})
        resp = await client.delete(
            f"/bookings/{booking_id}",
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled_late_by_client"

    async def test_waive_penalty_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Coach exonère la pénalité d'annulation tardive."""
        await _create_coach_profile(client, coach_api_key)
        resp = await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _future_slot(2)},
            headers={"X-API-Key": client_api_key},
        )
        booking_id = resp.json()["id"]
        await client.post(f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_api_key})
        await client.delete(f"/bookings/{booking_id}", headers={"X-API-Key": client_api_key})
        resp = await client.post(
            f"/bookings/{booking_id}/waive-penalty", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 200
        assert resp.json()["late_cancel_waived"] is True

    async def test_mark_done_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Coach marque une séance comme terminée."""
        booking_id = await self._setup_booking(client, coach_api_key, coach_user, client_api_key)
        await client.post(f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_api_key})
        resp = await client.post(f"/bookings/{booking_id}/done", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"

    async def test_no_show_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Coach marque un no-show."""
        booking_id = await self._setup_booking(client, coach_api_key, coach_user, client_api_key)
        await client.post(f"/bookings/{booking_id}/confirm", headers={"X-API-Key": coach_api_key})
        resp = await client.post(f"/bookings/{booking_id}/no-show", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert resp.json()["status"] == "no_show_client"

    async def test_wrong_coach_cannot_confirm(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
        db: AsyncSession,
    ):
        """❌ Un autre coach ne peut pas confirmer → 403."""
        booking_id = await self._setup_booking(client, coach_api_key, coach_user, client_api_key)
        # Créer un 2e coach
        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        other_coach = await user_repository.create(
            db, first_name="Other", last_name="Coach",
            email=f"other_{uuid.uuid4().hex[:6]}@test.com",
            role="coach", password_plain="Password1"
        )
        await db.commit()
        plain_key, _ = await api_key_repository.create(db, other_coach.id, "d2")
        await db.commit()
        resp = await client.post(
            f"/bookings/{booking_id}/confirm",
            headers={"X-API-Key": plain_key}
        )
        assert resp.status_code == 403


class TestBookingListing:
    async def test_list_bookings_client(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Client voit ses réservations."""
        await _create_coach_profile(client, coach_api_key)
        await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _future_slot()},
            headers={"X-API-Key": client_api_key},
        )
        resp = await client.get("/bookings", headers={"X-API-Key": client_api_key})
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    async def test_list_bookings_coach(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
    ):
        """✅ Coach voit ses réservations."""
        await _create_coach_profile(client, coach_api_key)
        await client.post(
            "/bookings",
            json={"coach_id": str(coach_user.id), "scheduled_at": _future_slot()},
            headers={"X-API-Key": client_api_key},
        )
        resp = await client.get("/bookings", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

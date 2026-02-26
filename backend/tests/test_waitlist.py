"""Tests Phase 2 — Liste d'attente — B2-26."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

BASE_COACH = {"bio": "Coach test", "currency": "EUR", "session_duration_min": 60}


def _future_slot(hours: int = 48) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


async def _setup(client, coach_key, client_key, coach_user):
    """Crée un profil coach + réserve et remplit un créneau."""
    await client.post("/coaches/profile", json=BASE_COACH, headers={"X-API-Key": coach_key})
    slot = _future_slot()
    # Réserver le créneau
    resp = await client.post(
        "/bookings",
        json={"coach_id": str(coach_user.id), "scheduled_at": slot},
        headers={"X-API-Key": client_key},
    )
    return slot, resp.json()["id"]


class TestWaitlist:
    async def test_join_waitlist_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
        db,
    ):
        """✅ Rejoindre la liste d'attente quand le créneau est plein."""
        slot, _ = await _setup(client, coach_api_key, client_api_key, coach_user)

        # Créer un 2e client pour rejoindre la file
        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        client2 = await user_repository.create(
            db, first_name="Wait", last_name="List",
            email=f"wl_{uuid.uuid4().hex[:6]}@test.com",
            role="client", password_plain="Password1"
        )
        await db.commit()
        key2, _ = await api_key_repository.create(db, client2.id, "d")
        await db.commit()

        resp = await client.post(
            "/waitlist",
            json={"coach_id": str(coach_user.id), "slot_datetime": slot},
            headers={"X-API-Key": key2},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["position"] == 1
        assert data["status"] == "waiting"

    async def test_join_waitlist_duplicate(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
        db,
    ):
        """❌ Rejoindre deux fois le même créneau → 409."""
        slot, _ = await _setup(client, coach_api_key, client_api_key, coach_user)

        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        wl_client = await user_repository.create(
            db, first_name="Dup", last_name="WL",
            email=f"dup_{uuid.uuid4().hex[:6]}@test.com",
            role="client", password_plain="Password1"
        )
        await db.commit()
        wl_key, _ = await api_key_repository.create(db, wl_client.id, "d")
        await db.commit()

        payload = {"coach_id": str(coach_user.id), "slot_datetime": slot}
        r1 = await client.post("/waitlist", json=payload, headers={"X-API-Key": wl_key})
        assert r1.status_code == 201
        r2 = await client.post("/waitlist", json=payload, headers={"X-API-Key": wl_key})
        assert r2.status_code == 409

    async def test_leave_waitlist_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
        db,
    ):
        """✅ Quitter la liste d'attente."""
        slot, _ = await _setup(client, coach_api_key, client_api_key, coach_user)

        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        wl_client = await user_repository.create(
            db, first_name="Lea", last_name="Ve",
            email=f"leave_{uuid.uuid4().hex[:6]}@test.com",
            role="client", password_plain="Password1"
        )
        await db.commit()
        wl_key, _ = await api_key_repository.create(db, wl_client.id, "d")
        await db.commit()

        join_resp = await client.post(
            "/waitlist",
            json={"coach_id": str(coach_user.id), "slot_datetime": slot},
            headers={"X-API-Key": wl_key},
        )
        entry_id = join_resp.json()["id"]

        del_resp = await client.delete(
            f"/waitlist/{entry_id}", headers={"X-API-Key": wl_key}
        )
        assert del_resp.status_code == 200

        # Vérifier la file est vide
        list_resp = await client.get("/waitlist", headers={"X-API-Key": wl_key})
        assert list_resp.status_code == 200
        assert list_resp.json() == []

    async def test_leave_other_entry_denied(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
        db,
    ):
        """❌ Quitter l'entrée d'un autre client → 404."""
        slot, _ = await _setup(client, coach_api_key, client_api_key, coach_user)

        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        wl1 = await user_repository.create(
            db, first_name="Wl", last_name="One",
            email=f"w1_{uuid.uuid4().hex[:6]}@test.com",
            role="client", password_plain="Password1"
        )
        wl2 = await user_repository.create(
            db, first_name="Wl", last_name="Two",
            email=f"w2_{uuid.uuid4().hex[:6]}@test.com",
            role="client", password_plain="Password1"
        )
        await db.commit()
        key1, _ = await api_key_repository.create(db, wl1.id, "d")
        key2, _ = await api_key_repository.create(db, wl2.id, "d")
        await db.commit()

        join = await client.post(
            "/waitlist",
            json={"coach_id": str(coach_user.id), "slot_datetime": slot},
            headers={"X-API-Key": key1},
        )
        entry_id = join.json()["id"]
        # wl2 essaie de supprimer l'entrée de wl1
        resp = await client.delete(f"/waitlist/{entry_id}", headers={"X-API-Key": key2})
        assert resp.status_code == 404

    async def test_my_waitlist_entries(
        self,
        client: AsyncClient,
        coach_api_key: str,
        coach_user,
        client_api_key: str,
        db,
    ):
        """✅ Lister mes entrées en file d'attente."""
        slot, _ = await _setup(client, coach_api_key, client_api_key, coach_user)

        from app.repositories.user_repository import user_repository
        from app.repositories.api_key_repository import api_key_repository
        wl_client = await user_repository.create(
            db, first_name="My", last_name="Wait",
            email=f"mw_{uuid.uuid4().hex[:6]}@test.com",
            role="client", password_plain="Password1"
        )
        await db.commit()
        wl_key, _ = await api_key_repository.create(db, wl_client.id, "d")
        await db.commit()

        await client.post(
            "/waitlist",
            json={"coach_id": str(coach_user.id), "slot_datetime": slot},
            headers={"X-API-Key": wl_key},
        )
        resp = await client.get("/waitlist", headers={"X-API-Key": wl_key})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

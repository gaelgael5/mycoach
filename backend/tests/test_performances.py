"""Tests Phase 3 — Performances, exercices, PRs — B3-15."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

BASE_PROFILE = {"bio": "Coach test", "currency": "EUR", "session_duration_min": 60}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _days_ago_iso(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


async def _seed_exercise(db: AsyncSession) -> uuid.UUID:
    """Seed un exercice de test et retourne son UUID."""
    from app.models.exercise_type import ExerciseType, ExerciseTypeMuscle
    et = ExerciseType(
        id=uuid.uuid4(),
        name_key=f"exercise.test_{uuid.uuid4().hex[:6]}",
        category="strength",
        difficulty="beginner",
        active=True,
    )
    db.add(et)
    muscle = ExerciseTypeMuscle(
        id=uuid.uuid4(),
        exercise_type_id=et.id,
        muscle_group="chest",
        role="primary",
    )
    db.add(muscle)
    await db.flush()
    return et.id


class TestPerformanceSessionCRUD:
    async def test_create_session_ok(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Créer une session vide."""
        resp = await client.post(
            "/performances",
            json={"session_type": "solo_free", "session_date": _now_iso()},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["session_type"] == "solo_free"
        assert data["exercise_sets"] == []

    async def test_create_session_with_sets(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Créer une session avec des sets."""
        ex_id = await _seed_exercise(db)
        await db.commit()
        resp = await client.post(
            "/performances",
            json={
                "session_type": "solo_free",
                "session_date": _now_iso(),
                "feeling": 4,
                "exercise_sets": [
                    {
                        "exercise_type_id": str(ex_id),
                        "set_order": 1,
                        "sets_count": 3,
                        "reps": 10,
                        "weight_kg": "60.00",
                    }
                ],
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["exercise_sets"]) == 1
        assert data["exercise_sets"][0]["reps"] == 10
        assert data["feeling"] == 4

    async def test_create_session_invalid_type(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ session_type invalide → 422."""
        resp = await client.post(
            "/performances",
            json={"session_type": "flying_solo", "session_date": _now_iso()},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_list_sessions_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Lister ses sessions."""
        await client.post(
            "/performances",
            json={"session_type": "solo_free", "session_date": _now_iso()},
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get("/performances", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1

    async def test_update_session_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Modifier une session (dans les 48h)."""
        create = await client.post(
            "/performances",
            json={"session_type": "solo_free", "session_date": _now_iso()},
            headers={"X-API-Key": coach_api_key},
        )
        sid = create.json()["id"]
        resp = await client.put(
            f"/performances/{sid}",
            json={"feeling": 5},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        assert resp.json()["feeling"] == 5

    async def test_delete_session_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Supprimer une session (dans les 48h)."""
        create = await client.post(
            "/performances",
            json={"session_type": "solo_free", "session_date": _now_iso()},
            headers={"X-API-Key": coach_api_key},
        )
        sid = create.json()["id"]
        resp = await client.delete(
            f"/performances/{sid}", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 200

    async def test_delete_other_user_session(
        self,
        client: AsyncClient,
        coach_api_key: str,
        client_api_key: str,
    ):
        """❌ Supprimer la session d'un autre utilisateur → 403."""
        create = await client.post(
            "/performances",
            json={"session_type": "solo_free", "session_date": _now_iso()},
            headers={"X-API-Key": coach_api_key},
        )
        sid = create.json()["id"]
        resp = await client.delete(
            f"/performances/{sid}", headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 403

    async def test_delete_nonexistent_session(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Session inexistante → 404."""
        resp = await client.delete(
            f"/performances/{uuid.uuid4()}", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 404

    async def test_update_expired_window(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """❌ Modifier une session de plus de 48h → 422."""
        # Créer directement en DB avec un created_at ancien
        from app.models.performance_session import PerformanceSession
        from app.models.user import User
        from sqlalchemy import select
        coach_q = select(User).where(User.role == "coach")
        coach = (await db.execute(coach_q)).scalar_one()
        old_session = PerformanceSession(
            id=uuid.uuid4(),
            user_id=coach.id,
            session_type="solo_free",
            session_date=datetime.now(timezone.utc) - timedelta(days=5),
            created_at=datetime.now(timezone.utc) - timedelta(hours=50),
        )
        db.add(old_session)
        await db.commit()

        resp = await client.put(
            f"/performances/{old_session.id}",
            json={"feeling": 3},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_no_auth(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/performances")
        assert resp.status_code == 401


class TestPersonalRecords:
    async def test_pr_detected_on_create(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Premier set = PR automatique."""
        ex_id = await _seed_exercise(db)
        await db.commit()
        resp = await client.post(
            "/performances",
            json={
                "session_type": "solo_free",
                "session_date": _now_iso(),
                "exercise_sets": [
                    {
                        "exercise_type_id": str(ex_id),
                        "set_order": 1, "sets_count": 3,
                        "reps": 8, "weight_kg": "80.00",
                    }
                ],
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        assert resp.json()["exercise_sets"][0]["is_pr"] is True

    async def test_pr_not_detected_if_lower(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ 2e set avec poids inférieur → pas de PR."""
        ex_id = await _seed_exercise(db)
        await db.commit()
        # 1ère session : 80kg (PR)
        await client.post(
            "/performances",
            json={
                "session_date": _days_ago_iso(7),
                "session_type": "solo_free",
                "exercise_sets": [{"exercise_type_id": str(ex_id),
                                    "set_order": 1, "sets_count": 3,
                                    "reps": 8, "weight_kg": "80.00"}],
            },
            headers={"X-API-Key": coach_api_key},
        )
        # 2e session : 70kg → pas de PR
        resp = await client.post(
            "/performances",
            json={
                "session_date": _now_iso(),
                "session_type": "solo_free",
                "exercise_sets": [{"exercise_type_id": str(ex_id),
                                    "set_order": 1, "sets_count": 3,
                                    "reps": 8, "weight_kg": "70.00"}],
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.json()["exercise_sets"][0]["is_pr"] is False

    async def test_get_personal_records(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Lister les PRs."""
        ex_id = await _seed_exercise(db)
        await db.commit()
        await client.post(
            "/performances",
            json={
                "session_date": _now_iso(), "session_type": "solo_free",
                "exercise_sets": [{"exercise_type_id": str(ex_id),
                                    "set_order": 1, "sets_count": 1,
                                    "reps": 5, "weight_kg": "100.00"}],
            },
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.get("/performances/personal-records", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        prs = resp.json()
        assert len(prs) >= 1
        assert prs[0]["weight_kg"] == "100.00"


class TestCoachSessionForClient:
    async def test_coach_can_enter_for_client(
        self,
        client: AsyncClient,
        coach_api_key: str,
        client_user,
    ):
        """✅ Coach saisit les performances pour un client."""
        resp = await client.post(
            f"/performances/for-client/{client_user.id}",
            json={"session_type": "coached", "session_date": _now_iso()},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["user_id"] == str(client_user.id)
        assert data["session_type"] == "coached"

    async def test_client_cannot_use_for_client_endpoint(
        self,
        client: AsyncClient,
        client_api_key: str,
        coach_user,
    ):
        """❌ Client ne peut pas utiliser le endpoint coach → 403."""
        resp = await client.post(
            f"/performances/for-client/{coach_user.id}",
            json={"session_type": "coached", "session_date": _now_iso()},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 403


class TestExerciseEndpoints:
    async def test_list_exercises_empty(self, client: AsyncClient):
        """✅ Liste vide sans données."""
        resp = await client.get("/exercises")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    async def test_list_exercises_with_data(
        self, client: AsyncClient, db: AsyncSession
    ):
        """✅ Liste avec données seedées."""
        for name in ["exercise.squat", "exercise.bench_press"]:
            from app.models.exercise_type import ExerciseType
            et = ExerciseType(
                id=uuid.uuid4(), name_key=name,
                category="strength", difficulty="intermediate", active=True
            )
            db.add(et)
        await db.commit()

        resp = await client.get("/exercises")
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    async def test_filter_by_category(self, client: AsyncClient, db: AsyncSession):
        """✅ Filtrer par catégorie."""
        from app.models.exercise_type import ExerciseType
        for name, cat in [("exercise.run", "cardio"), ("exercise.squat2", "strength")]:
            db.add(ExerciseType(id=uuid.uuid4(), name_key=name, category=cat,
                                difficulty="beginner", active=True))
        await db.commit()

        resp = await client.get("/exercises?category=cardio")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    async def test_exercises_public(self, client: AsyncClient):
        """✅ Exercices accessibles sans auth."""
        resp = await client.get("/exercises")
        assert resp.status_code == 200

    async def test_get_exercise_not_found(self, client: AsyncClient):
        """❌ ID inconnu → 404."""
        resp = await client.get(f"/exercises/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestWeekStats:
    async def test_week_stats_empty(self, client: AsyncClient, coach_api_key: str):
        """✅ Stats de semaine vides."""
        # Lundi de la semaine courante
        now = datetime.now(timezone.utc)
        monday = now - timedelta(days=now.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        resp = await client.get(
            "/performances/stats/week",
            params={"week_start": monday.isoformat()},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["sessions_count"] == 0
        assert data["total_sets"] == 0
        assert data["muscles_worked"] == []

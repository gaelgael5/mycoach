"""Tests Phase 4 — Programmes d'entraînement — B4-13."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

BASE_PROFILE = {"bio": "Coach test", "currency": "EUR", "session_duration_min": 60}

PLAN_DATA = {
    "name": "Programme Test",
    "duration_weeks": 4,
    "level": "beginner",
    "goal": "muscle_gain",
    "planned_sessions": [
        {
            "day_of_week": 0,
            "session_name": "Push Day",
            "estimated_duration_min": 60,
            "rest_seconds": 90,
            "planned_exercises": [],
        }
    ],
}


async def _seed_exercise(db: AsyncSession) -> uuid.UUID:
    from app.models.exercise_type import ExerciseType
    et = ExerciseType(
        id=uuid.uuid4(),
        name_key=f"exercise.prog_{uuid.uuid4().hex[:6]}",
        category="strength",
        difficulty="beginner",
        active=True,
    )
    db.add(et)
    await db.flush()
    return et.id


class TestCoachPlanCRUD:
    async def test_create_plan_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Créer un plan."""
        await client.post("/coaches/profile", json=BASE_PROFILE, headers={"X-API-Key": coach_api_key})
        resp = await client.post(
            "/coaches/programs", json=PLAN_DATA, headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Programme Test"
        assert data["is_ai_generated"] is False
        assert len(data["planned_sessions"]) == 1

    async def test_create_plan_invalid_level(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Niveau invalide → 422."""
        resp = await client.post(
            "/coaches/programs",
            json={**PLAN_DATA, "level": "expert"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_create_plan_invalid_goal(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Objectif invalide → 422."""
        resp = await client.post(
            "/coaches/programs",
            json={**PLAN_DATA, "goal": "become_arnold"},
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_list_plans_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Lister les plans du coach."""
        await client.post("/coaches/programs", json=PLAN_DATA, headers={"X-API-Key": coach_api_key})
        resp = await client.get("/coaches/programs", headers={"X-API-Key": coach_api_key})
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["sessions_count"] == 1

    async def test_get_plan_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ GET /coaches/programs/{id}."""
        create = await client.post(
            "/coaches/programs", json=PLAN_DATA, headers={"X-API-Key": coach_api_key}
        )
        plan_id = create.json()["id"]
        resp = await client.get(
            f"/coaches/programs/{plan_id}", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == plan_id

    async def test_get_plan_not_found(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Plan inexistant → 404."""
        resp = await client.get(
            f"/coaches/programs/{uuid.uuid4()}", headers={"X-API-Key": coach_api_key}
        )
        assert resp.status_code == 404

    async def test_archive_plan_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Archiver un plan."""
        create = await client.post(
            "/coaches/programs", json=PLAN_DATA, headers={"X-API-Key": coach_api_key}
        )
        plan_id = create.json()["id"]
        resp = await client.post(
            f"/coaches/programs/{plan_id}/archive",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        # Plan archivé absent par défaut de la liste
        lst = await client.get("/coaches/programs", headers={"X-API-Key": coach_api_key})
        assert not any(p["id"] == plan_id for p in lst.json())

    async def test_archive_already_archived(
        self, client: AsyncClient, coach_api_key: str
    ):
        """❌ Archiver deux fois → 422."""
        create = await client.post(
            "/coaches/programs", json=PLAN_DATA, headers={"X-API-Key": coach_api_key}
        )
        plan_id = create.json()["id"]
        await client.post(
            f"/coaches/programs/{plan_id}/archive",
            headers={"X-API-Key": coach_api_key},
        )
        resp = await client.post(
            f"/coaches/programs/{plan_id}/archive",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 422

    async def test_duplicate_plan_ok(
        self, client: AsyncClient, coach_api_key: str
    ):
        """✅ Dupliquer un plan."""
        create = await client.post(
            "/coaches/programs", json=PLAN_DATA, headers={"X-API-Key": coach_api_key}
        )
        plan_id = create.json()["id"]
        resp = await client.post(
            f"/coaches/programs/{plan_id}/duplicate",
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "(copie)" in data["name"]
        assert data["id"] != plan_id

    async def test_client_cannot_manage_plans(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Client ne peut pas créer de plans → 403."""
        resp = await client.post(
            "/coaches/programs", json=PLAN_DATA, headers={"X-API-Key": client_api_key}
        )
        assert resp.status_code == 403

    async def test_no_auth(self, client: AsyncClient):
        """❌ Sans clé API → 401."""
        resp = await client.get("/coaches/programs")
        assert resp.status_code == 401


class TestAiProgramGeneration:
    async def test_generate_program_ok(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """✅ Générer un programme IA (sans exercices en base → plan vide mais valide)."""
        resp = await client.post(
            "/clients/program/generate",
            json={"goal": "muscle_gain", "frequency_per_week": 3, "level": "beginner"},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["workout_plan"]["is_ai_generated"] is True
        assert data["workout_plan"]["goal"] == "muscle_gain"
        assert data["active"] is True

    async def test_generate_program_with_exercises(
        self, client: AsyncClient, client_api_key: str, db: AsyncSession
    ):
        """✅ Programme IA intègre des exercices existants."""
        # Seed exercices de force débutant
        from app.models.exercise_type import ExerciseType, ExerciseTypeMuscle
        for name, cat, muscle in [
            ("exercise.p3_squat", "strength", "quads"),
            ("exercise.p3_bench", "strength", "chest"),
            ("exercise.p3_row", "strength", "back"),
            ("exercise.p3_cardio", "cardio", "full_body"),
            ("exercise.p3_yoga", "yoga", "full_body"),
        ]:
            et = ExerciseType(id=uuid.uuid4(), name_key=name,
                              category=cat, difficulty="beginner", active=True)
            db.add(et)
            await db.flush()
            db.add(ExerciseTypeMuscle(
                id=uuid.uuid4(), exercise_type_id=et.id,
                muscle_group=muscle, role="primary"
            ))
        await db.commit()

        resp = await client.post(
            "/clients/program/generate",
            json={"goal": "well_being", "frequency_per_week": 3, "level": "beginner"},
            headers={"X-API-Key": client_api_key},
        )
        assert resp.status_code == 201
        plan = resp.json()["workout_plan"]
        assert plan["is_ai_generated"] is True

    async def test_get_my_program_none(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Aucun programme → null."""
        resp = await client.get("/clients/program", headers={"X-API-Key": client_api_key})
        assert resp.status_code == 200
        assert resp.json() is None

    async def test_get_my_program_after_generate(
        self, client: AsyncClient, client_api_key: str
    ):
        """✅ Programme récupéré après génération."""
        await client.post(
            "/clients/program/generate",
            json={"goal": "endurance", "frequency_per_week": 3, "level": "beginner"},
            headers={"X-API-Key": client_api_key},
        )
        resp = await client.get("/clients/program", headers={"X-API-Key": client_api_key})
        assert resp.status_code == 200
        assert resp.json() is not None
        assert resp.json()["active"] is True

    async def test_invalid_goal(
        self, client: AsyncClient, client_api_key: str
    ):
        """❌ Objectif inconnu → programme fallback (pas d'erreur)."""
        resp = await client.post(
            "/clients/program/generate",
            json={"goal": "unknown", "frequency_per_week": 3, "level": "beginner"},
            headers={"X-API-Key": client_api_key},
        )
        # Le générateur tombe sur le fallback "well_being" → 201
        assert resp.status_code == 201


class TestPlanAssignment:
    async def test_assign_plan_ok(
        self,
        client: AsyncClient,
        coach_api_key: str,
        client_user,
    ):
        """✅ Coach assigne un plan à un client."""
        create = await client.post(
            "/coaches/programs", json=PLAN_DATA, headers={"X-API-Key": coach_api_key}
        )
        plan_id = create.json()["id"]
        resp = await client.post(
            f"/coaches/programs/{plan_id}/assign",
            json={
                "client_id": str(client_user.id),
                "start_date": str(date.today()),
                "mode": "replace_ai",
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["client_id"] == str(client_user.id)
        assert data["active"] is True

    async def test_assign_nonexistent_plan(
        self,
        client: AsyncClient,
        coach_api_key: str,
        client_user,
    ):
        """❌ Assigner un plan inexistant → 404."""
        resp = await client.post(
            f"/coaches/programs/{uuid.uuid4()}/assign",
            json={
                "client_id": str(client_user.id),
                "start_date": str(date.today()),
            },
            headers={"X-API-Key": coach_api_key},
        )
        assert resp.status_code == 404


class TestProgressionService:
    async def test_no_plan_no_adjustment(
        self, client: AsyncClient, coach_api_key: str, db: AsyncSession
    ):
        """✅ Pas de plan actif → pas d'ajustement."""
        from app.models.user import User
        from sqlalchemy import select
        coach = (await db.execute(select(User).where(User.role == "coach"))).scalar_one()
        from app.services.progression_service import check_and_adjust
        result = await check_and_adjust(db, coach.id, uuid.uuid4())
        assert result is None

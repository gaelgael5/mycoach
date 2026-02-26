"""Service programmes d'entraînement — B4-10."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import program_repository as repo
from app.schemas.program import (
    WorkoutPlanCreate, WorkoutPlanUpdate,
    PlannedSessionCreate, PlannedExerciseCreate,
)


class PlanNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


class PlanAlreadyArchivedError(Exception):
    pass


# ── CRUD plans ─────────────────────────────────────────────────────────────────

async def create_plan(
    db: AsyncSession, coach: User, data: WorkoutPlanCreate
) -> object:
    plan = await repo.create_plan(
        db,
        created_by_id=coach.id,
        is_ai_generated=False,
        name=data.name,
        description=data.description,
        duration_weeks=data.duration_weeks,
        level=data.level,
        goal=data.goal,
    )
    for idx, session_data in enumerate(data.planned_sessions):
        ps = await repo.add_planned_session(
            db, plan.id,
            day_of_week=session_data.day_of_week,
            session_name=session_data.session_name,
            estimated_duration_min=session_data.estimated_duration_min,
            rest_seconds=session_data.rest_seconds,
            order_index=idx + 1,
        )
        for ex_idx, ex_data in enumerate(session_data.planned_exercises):
            await repo.add_planned_exercise(
                db, ps.id,
                exercise_type_id=ex_data.exercise_type_id,
                target_sets=ex_data.target_sets,
                target_reps=ex_data.target_reps,
                target_weight_kg=ex_data.target_weight_kg,
                order_index=ex_idx + 1,
            )
    return await repo.get_plan_by_id(db, plan.id)


async def list_plans(
    db: AsyncSession, coach: User, *, include_archived: bool = False
) -> list:
    return await repo.list_plans_by_coach(db, coach.id, include_archived=include_archived)


async def get_plan(db: AsyncSession, coach: User, plan_id: uuid.UUID) -> object:
    plan = await repo.get_plan_by_id(db, plan_id)
    if plan is None:
        raise PlanNotFoundError("Plan introuvable")
    if plan.created_by_id != coach.id and not plan.is_ai_generated:
        raise NotAuthorizedError("Ce plan ne vous appartient pas")
    return plan


async def archive_plan(db: AsyncSession, coach: User, plan_id: uuid.UUID) -> object:
    plan = await repo.get_plan_by_id(db, plan_id)
    if plan is None:
        raise PlanNotFoundError("Plan introuvable")
    if plan.created_by_id != coach.id:
        raise NotAuthorizedError("Ce plan ne vous appartient pas")
    if plan.archived:
        raise PlanAlreadyArchivedError("Plan déjà archivé")
    return await repo.archive_plan(db, plan)


async def duplicate_plan(db: AsyncSession, coach: User, plan_id: uuid.UUID) -> object:
    """Duplique un plan (coach) sous un nouveau nom."""
    source = await repo.get_plan_by_id(db, plan_id)
    if source is None:
        raise PlanNotFoundError("Plan introuvable")
    new_plan = await repo.create_plan(
        db,
        created_by_id=coach.id,
        is_ai_generated=False,
        name=f"{source.name} (copie)",
        description=source.description,
        duration_weeks=source.duration_weeks,
        level=source.level,
        goal=source.goal,
    )
    for ps in source.planned_sessions:
        new_ps = await repo.add_planned_session(
            db, new_plan.id,
            day_of_week=ps.day_of_week,
            session_name=ps.session_name,
            estimated_duration_min=ps.estimated_duration_min,
            rest_seconds=ps.rest_seconds,
            order_index=ps.order_index,
        )
        for pe in ps.planned_exercises:
            await repo.add_planned_exercise(
                db, new_ps.id,
                exercise_type_id=pe.exercise_type_id,
                target_sets=pe.target_sets,
                target_reps=pe.target_reps,
                target_weight_kg=pe.target_weight_kg,
                order_index=pe.order_index,
            )
    return await repo.get_plan_by_id(db, new_plan.id)


# ── Assignation ────────────────────────────────────────────────────────────────

async def assign_to_client(
    db: AsyncSession,
    coach: User,
    plan_id: uuid.UUID,
    client_id: uuid.UUID,
    start_date: date,
    mode: str = "replace_ai",
) -> object:
    plan = await repo.get_plan_by_id(db, plan_id)
    if plan is None:
        raise PlanNotFoundError("Plan introuvable")
    return await repo.assign_plan(
        db,
        plan_id=plan_id,
        client_id=client_id,
        start_date=start_date,
        mode=mode,
        assigned_by_id=coach.id,
    )


async def get_client_progress(
    db: AsyncSession, coach: User, client_id: uuid.UUID, plan_id: uuid.UUID
) -> dict:
    return await repo.get_client_progress(db, client_id, plan_id)


# ── Programme client courant ───────────────────────────────────────────────────

async def get_my_program(db: AsyncSession, client: User) -> object | None:
    """Retourne le plan actif du client (généré IA ou assigné par coach)."""
    return await repo.get_current_assignment(db, client.id)


async def recalibrate_my_program(
    db: AsyncSession, client: User
) -> object:
    """Régénère un programme IA pour le client selon son questionnaire actuel."""
    from app.repositories.client_repository import get_questionnaire
    from app.services.program_generator_service import generate_weekly_program

    questionnaire = await get_questionnaire(db, client.id)
    goal = questionnaire.goal if questionnaire else "well_being"
    freq = questionnaire.frequency_per_week if questionnaire else 3
    level_map = {"beginner": "beginner", "intermediate": "intermediate", "advanced": "advanced"}
    level = getattr(questionnaire, "level", "beginner") if questionnaire else "beginner"

    plan = await generate_weekly_program(
        db,
        goal=goal,
        frequency_per_week=freq,
        level=level_map.get(level, "beginner"),
        client_id=client.id,
    )
    # Assigner automatiquement
    today = date.today()
    await repo.assign_plan(
        db,
        plan_id=plan.id,
        client_id=client.id,
        start_date=today,
        mode="replace_ai",
        assigned_by_id=None,
    )
    return await repo.get_current_assignment(db, client.id)

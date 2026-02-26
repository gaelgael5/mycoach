"""Repository programmes d'entraînement — B4-09."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.workout_plan import (
    PlanAssignment, PlannedExercise, PlannedSession, WorkoutPlan
)


# ── Plans ──────────────────────────────────────────────────────────────────────

async def create_plan(
    db: AsyncSession, *, created_by_id: uuid.UUID | None, is_ai_generated: bool = False, **kwargs
) -> WorkoutPlan:
    plan = WorkoutPlan(
        id=uuid.uuid4(),
        created_by_id=created_by_id,
        is_ai_generated=is_ai_generated,
        **kwargs,
    )
    db.add(plan)
    await db.flush()
    return plan


async def get_plan_by_id(db: AsyncSession, plan_id: uuid.UUID) -> WorkoutPlan | None:
    q = (
        select(WorkoutPlan)
        .where(WorkoutPlan.id == plan_id)
        .options(
            selectinload(WorkoutPlan.planned_sessions).selectinload(
                PlannedSession.planned_exercises
            )
        )
    )
    return (await db.execute(q)).scalar_one_or_none()


async def list_plans_by_coach(
    db: AsyncSession, coach_id: uuid.UUID, *, include_archived: bool = False
) -> list[WorkoutPlan]:
    q = select(WorkoutPlan).where(WorkoutPlan.created_by_id == coach_id)
    if not include_archived:
        q = q.where(WorkoutPlan.archived.is_(False))
    q = q.options(
        selectinload(WorkoutPlan.planned_sessions).selectinload(PlannedSession.planned_exercises)
    ).order_by(WorkoutPlan.created_at.desc())
    return list((await db.execute(q)).scalars().all())


async def archive_plan(db: AsyncSession, plan: WorkoutPlan) -> WorkoutPlan:
    plan.archived = True
    await db.flush()
    return plan


async def add_planned_session(
    db: AsyncSession, plan_id: uuid.UUID, **kwargs
) -> PlannedSession:
    ps = PlannedSession(id=uuid.uuid4(), plan_id=plan_id, **kwargs)
    db.add(ps)
    await db.flush()
    return ps


async def add_planned_exercise(
    db: AsyncSession, session_id: uuid.UUID, **kwargs
) -> PlannedExercise:
    pe = PlannedExercise(id=uuid.uuid4(), planned_session_id=session_id, **kwargs)
    db.add(pe)
    await db.flush()
    return pe


# ── Assignations ───────────────────────────────────────────────────────────────

async def assign_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
    client_id: uuid.UUID,
    start_date: date,
    mode: str,
    assigned_by_id: uuid.UUID | None,
) -> PlanAssignment:
    # Désactiver les assignations précédentes si mode replace_ai
    if mode == "replace_ai":
        q = select(PlanAssignment).where(
            PlanAssignment.client_id == client_id,
            PlanAssignment.active.is_(True),
        )
        for old in (await db.execute(q)).scalars().all():
            old.active = False
    assignment = PlanAssignment(
        id=uuid.uuid4(),
        plan_id=plan_id,
        client_id=client_id,
        start_date=start_date,
        mode=mode,
        assigned_by_id=assigned_by_id,
        active=True,
    )
    db.add(assignment)
    await db.flush()
    return assignment


async def get_assignment_by_id(
    db: AsyncSession, assignment_id: uuid.UUID
) -> PlanAssignment | None:
    q = (
        select(PlanAssignment)
        .where(PlanAssignment.id == assignment_id)
        .options(
            joinedload(PlanAssignment.workout_plan).selectinload(
                WorkoutPlan.planned_sessions
            ).selectinload(PlannedSession.planned_exercises)
        )
    )
    return (await db.execute(q)).unique().scalar_one_or_none()


async def get_current_assignment(
    db: AsyncSession, client_id: uuid.UUID
) -> PlanAssignment | None:
    q = (
        select(PlanAssignment)
        .where(PlanAssignment.client_id == client_id, PlanAssignment.active.is_(True))
        .options(
            # joinedload pour la relation N:1 PlanAssignment → WorkoutPlan
            joinedload(PlanAssignment.workout_plan).selectinload(
                WorkoutPlan.planned_sessions
            ).selectinload(PlannedSession.planned_exercises)
        )
        .order_by(PlanAssignment.created_at.desc())
        .limit(1)
    )
    return (await db.execute(q)).unique().scalar_one_or_none()


# ── Progression ────────────────────────────────────────────────────────────────

async def get_client_progress(
    db: AsyncSession, client_id: uuid.UUID, plan_id: uuid.UUID
) -> dict:
    """Retourne le nombre de séances réalisées vs planifiées (approximation)."""
    plan = await get_plan_by_id(db, plan_id)
    if plan is None:
        return {"planned_sessions": 0, "completed_sessions": 0, "completion_pct": 0}

    planned_count = len(plan.planned_sessions)

    # Séances réelles liées au plan (via booking ou session type coached)
    from app.models.performance_session import PerformanceSession
    q = (
        select(func.count(PerformanceSession.id))
        .where(PerformanceSession.user_id == client_id)
    )
    completed = (await db.execute(q)).scalar_one()
    pct = round(completed / max(planned_count, 1) * 100, 1)
    return {
        "planned_sessions": planned_count,
        "completed_sessions": completed,
        "completion_pct": pct,
    }

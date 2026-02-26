"""Repository performances — B3-10."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.exercise_set import ExerciseSet
from app.models.exercise_type import ExerciseType, ExerciseTypeMuscle
from app.models.performance_session import PerformanceSession


# ── Sessions ──────────────────────────────────────────────────────────────────

async def create_session(
    db: AsyncSession, user_id: uuid.UUID, **kwargs
) -> PerformanceSession:
    session = PerformanceSession(id=uuid.uuid4(), user_id=user_id, **kwargs)
    db.add(session)
    await db.flush()
    return session


async def get_by_id(
    db: AsyncSession, session_id: uuid.UUID
) -> PerformanceSession | None:
    q = (
        select(PerformanceSession)
        .where(PerformanceSession.id == session_id)
        .options(selectinload(PerformanceSession.exercise_sets))
    )
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def update_session(
    db: AsyncSession,
    perf_session: PerformanceSession,
    **kwargs,
) -> PerformanceSession:
    for k, v in kwargs.items():
        if v is not None:
            setattr(perf_session, k, v)
    await db.flush()
    return perf_session


async def delete_session(db: AsyncSession, perf_session: PerformanceSession) -> None:
    await db.delete(perf_session)
    await db.flush()


async def get_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    session_type: str | None = None,
    gym_id: uuid.UUID | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[PerformanceSession], int]:
    q = (
        select(PerformanceSession)
        .where(PerformanceSession.user_id == user_id)
        .options(selectinload(PerformanceSession.exercise_sets))
    )
    if session_type:
        q = q.where(PerformanceSession.session_type == session_type)
    if gym_id:
        q = q.where(PerformanceSession.gym_id == gym_id)
    if from_date:
        q = q.where(PerformanceSession.session_date >= from_date)
    if to_date:
        q = q.where(PerformanceSession.session_date <= to_date)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    q = q.order_by(PerformanceSession.session_date.desc()).offset(offset).limit(limit)
    items = (await db.execute(q)).scalars().all()
    return list(items), total


# ── Exercise Sets ──────────────────────────────────────────────────────────────

async def add_set(
    db: AsyncSession, session_id: uuid.UUID, **kwargs
) -> ExerciseSet:
    ex_set = ExerciseSet(id=uuid.uuid4(), session_id=session_id, **kwargs)
    db.add(ex_set)
    await db.flush()
    return ex_set


async def replace_sets(
    db: AsyncSession,
    session: PerformanceSession,
    sets_data: list[dict],
) -> list[ExerciseSet]:
    """Remplace tous les sets d'une session (DELETE + INSERT)."""
    # Supprimer les anciens sets
    for ex_set in list(session.exercise_sets):
        await db.delete(ex_set)
    await db.flush()
    # Insérer les nouveaux
    new_sets = []
    for data in sets_data:
        ex_set = ExerciseSet(id=uuid.uuid4(), session_id=session.id, **data)
        db.add(ex_set)
        new_sets.append(ex_set)
    await db.flush()
    return new_sets


# ── Statistiques ──────────────────────────────────────────────────────────────

async def get_progression_stats(
    db: AsyncSession,
    user_id: uuid.UUID,
    exercise_type_id: uuid.UUID,
    *,
    limit: int = 20,
) -> list[dict]:
    """Retourne la progression (poids max + volume) par séance."""
    q = (
        select(
            PerformanceSession.session_date,
            func.max(ExerciseSet.weight_kg).label("max_weight_kg"),
            func.sum(ExerciseSet.weight_kg * ExerciseSet.reps).label("total_volume_kg"),
            func.count(ExerciseSet.id).label("sets_count"),
        )
        .join(ExerciseSet, ExerciseSet.session_id == PerformanceSession.id)
        .where(
            PerformanceSession.user_id == user_id,
            ExerciseSet.exercise_type_id == exercise_type_id,
        )
        .group_by(PerformanceSession.session_date)
        .order_by(PerformanceSession.session_date.desc())
        .limit(limit)
    )
    rows = (await db.execute(q)).all()
    return [
        {
            "session_date": r.session_date,
            "max_weight_kg": r.max_weight_kg,
            "total_volume_kg": r.total_volume_kg,
            "sets_count": r.sets_count,
        }
        for r in reversed(rows)  # chronologique
    ]


async def get_week_stats(
    db: AsyncSession,
    user_id: uuid.UUID,
    week_start: datetime,
) -> dict:
    """Stats pour une semaine donnée."""
    week_end = week_start + timedelta(days=7)
    q = (
        select(PerformanceSession)
        .where(
            PerformanceSession.user_id == user_id,
            PerformanceSession.session_date >= week_start,
            PerformanceSession.session_date < week_end,
        )
        .options(
            selectinload(PerformanceSession.exercise_sets).selectinload(
                ExerciseSet.exercise_type
            ).selectinload(ExerciseType.muscles)
        )
    )
    sessions = (await db.execute(q)).scalars().all()

    total_duration = sum(s.duration_min or 0 for s in sessions)
    feelings = [s.feeling for s in sessions if s.feeling]
    avg_feeling = sum(feelings) / len(feelings) if feelings else None
    total_sets = sum(len(s.exercise_sets) for s in sessions)

    # Groupes musculaires travaillés (uniques)
    muscles_worked: set[str] = set()
    for session in sessions:
        for ex_set in session.exercise_sets:
            for muscle in ex_set.exercise_type.muscles:
                if muscle.role == "primary":
                    muscles_worked.add(muscle.muscle_group)

    return {
        "week_start": week_start,
        "sessions_count": len(sessions),
        "total_duration_min": total_duration,
        "avg_feeling": avg_feeling,
        "total_sets": total_sets,
        "muscles_worked": sorted(muscles_worked),
    }


async def get_personal_records(
    db: AsyncSession, user_id: uuid.UUID
) -> list[dict]:
    """Retourne les PRs (is_pr=TRUE) de l'utilisateur."""
    q = (
        select(
            ExerciseSet,
            PerformanceSession.session_date,
            ExerciseType.name_key,
        )
        .join(PerformanceSession, ExerciseSet.session_id == PerformanceSession.id)
        .join(ExerciseType, ExerciseSet.exercise_type_id == ExerciseType.id)
        .where(
            PerformanceSession.user_id == user_id,
            ExerciseSet.is_pr.is_(True),
        )
        .order_by(PerformanceSession.session_date.desc())
    )
    rows = (await db.execute(q)).all()
    return [
        {
            "id": r.ExerciseSet.id,
            "exercise_type_id": r.ExerciseSet.exercise_type_id,
            "exercise_name_key": r.name_key,
            "weight_kg": r.ExerciseSet.weight_kg,
            "reps": r.ExerciseSet.reps,
            "achieved_at": r.session_date,
            "session_id": r.ExerciseSet.session_id,
        }
        for r in rows
    ]


# ── Détection PR ──────────────────────────────────────────────────────────────

async def get_max_weight_for_exercise(
    db: AsyncSession, user_id: uuid.UUID, exercise_type_id: uuid.UUID
) -> Decimal | None:
    """Retourne le poids max historique pour un exercice donné."""
    q = (
        select(func.max(ExerciseSet.weight_kg))
        .join(PerformanceSession, ExerciseSet.session_id == PerformanceSession.id)
        .where(
            PerformanceSession.user_id == user_id,
            ExerciseSet.exercise_type_id == exercise_type_id,
        )
    )
    return (await db.execute(q)).scalar_one_or_none()


# ── Exercise Types ────────────────────────────────────────────────────────────

async def search_exercises(
    db: AsyncSession,
    *,
    q: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    muscle: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[ExerciseType], int]:
    query = (
        select(ExerciseType)
        .where(ExerciseType.active.is_(True))
        .options(selectinload(ExerciseType.muscles))
    )
    if q:
        query = query.where(ExerciseType.name_key.ilike(f"%{q}%"))
    if category:
        query = query.where(ExerciseType.category == category)
    if difficulty:
        query = query.where(ExerciseType.difficulty == difficulty)
    if muscle:
        query = query.join(
            ExerciseTypeMuscle,
            ExerciseTypeMuscle.exercise_type_id == ExerciseType.id,
        ).where(ExerciseTypeMuscle.muscle_group == muscle)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    query = query.order_by(ExerciseType.name_key).offset(offset).limit(limit)
    items = (await db.execute(query)).scalars().unique().all()
    return list(items), total


async def get_exercise_by_id(
    db: AsyncSession, exercise_type_id: uuid.UUID
) -> ExerciseType | None:
    q = (
        select(ExerciseType)
        .where(ExerciseType.id == exercise_type_id)
        .options(selectinload(ExerciseType.muscles))
    )
    return (await db.execute(q)).scalar_one_or_none()

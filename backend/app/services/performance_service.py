"""Service performances — B3-11."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import performance_repository as repo
from app.schemas.performance import (
    PerformanceSessionCreate,
    PerformanceSessionUpdate,
)


class SessionNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


class EditWindowExpiredError(Exception):
    """Modification/suppression impossible au-delà de 48h."""
    pass


EDIT_WINDOW_HOURS = 48


def _assert_edit_window(session_created_at: datetime) -> None:
    """Vérifie qu'on est dans la fenêtre de 48h."""
    now = datetime.now(timezone.utc)
    created = session_created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    if (now - created) > timedelta(hours=EDIT_WINDOW_HOURS):
        raise EditWindowExpiredError(
            f"Modification impossible après {EDIT_WINDOW_HOURS}h"
        )


async def create_session(
    db: AsyncSession,
    user: User,
    data: PerformanceSessionCreate,
    *,
    entered_by_id: uuid.UUID | None = None,
) -> object:
    """Crée une session de performance avec ses sets.
    Détecte automatiquement les nouveaux PRs.
    """
    session = await repo.create_session(
        db,
        user_id=user.id,
        session_type=data.session_type,
        booking_id=data.booking_id,
        entered_by_id=entered_by_id,
        gym_id=data.gym_id,
        session_date=data.session_date,
        duration_min=data.duration_min,
        feeling=data.feeling,
    )

    # Ajouter les sets + détecter les PRs
    for set_data in data.exercise_sets:
        is_pr = False
        if set_data.weight_kg is not None:
            max_prev = await repo.get_max_weight_for_exercise(
                db, user.id, set_data.exercise_type_id
            )
            if max_prev is None or set_data.weight_kg > max_prev:
                is_pr = True

        await repo.add_set(
            db,
            session_id=session.id,
            exercise_type_id=set_data.exercise_type_id,
            machine_id=set_data.machine_id,
            set_order=set_data.set_order,
            sets_count=set_data.sets_count,
            reps=set_data.reps,
            weight_kg=set_data.weight_kg,
            notes=set_data.notes,
            is_pr=is_pr,
        )

    # TODO B2-17 : notifier si nouveau PR détecté

    # Recharger avec sets
    return await repo.get_by_id(db, session.id)


async def update_session(
    db: AsyncSession,
    user: User,
    session_id: uuid.UUID,
    data: PerformanceSessionUpdate,
) -> object:
    """Modifie une session (limité à 48h après création)."""
    session = await repo.get_by_id(db, session_id)
    if session is None:
        raise SessionNotFoundError("Session introuvable")
    if session.user_id != user.id:
        raise NotAuthorizedError("Pas votre session")
    _assert_edit_window(session.created_at)

    # Mise à jour des champs simples
    update_fields = {}
    if data.session_date is not None:
        update_fields["session_date"] = data.session_date
    if data.duration_min is not None:
        update_fields["duration_min"] = data.duration_min
    if data.feeling is not None:
        update_fields["feeling"] = data.feeling
    if update_fields:
        await repo.update_session(db, session, **update_fields)

    # Mise à jour des sets (replace all)
    if data.exercise_sets is not None:
        sets_dicts = [
            {
                "exercise_type_id": s.exercise_type_id,
                "machine_id": s.machine_id,
                "set_order": s.set_order,
                "sets_count": s.sets_count,
                "reps": s.reps,
                "weight_kg": s.weight_kg,
                "notes": s.notes,
                "is_pr": False,  # recalcul simplifié
            }
            for s in data.exercise_sets
        ]
        await repo.replace_sets(db, session, sets_dicts)

    return await repo.get_by_id(db, session_id)


async def delete_session(
    db: AsyncSession, user: User, session_id: uuid.UUID
) -> None:
    """Supprime une session (limité à 48h après création)."""
    session = await repo.get_by_id(db, session_id)
    if session is None:
        raise SessionNotFoundError("Session introuvable")
    if session.user_id != user.id:
        raise NotAuthorizedError("Pas votre session")
    _assert_edit_window(session.created_at)
    await repo.delete_session(db, session)


async def get_history(
    db: AsyncSession,
    user: User,
    *,
    session_type: str | None = None,
    gym_id: uuid.UUID | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list, int]:
    return await repo.get_history(
        db,
        user.id,
        session_type=session_type,
        gym_id=gym_id,
        from_date=from_date,
        to_date=to_date,
        offset=offset,
        limit=limit,
    )


async def get_progression(
    db: AsyncSession, user: User, exercise_type_id: uuid.UUID
) -> list:
    return await repo.get_progression_stats(db, user.id, exercise_type_id)


async def get_week_dashboard(
    db: AsyncSession, user: User, week_start: datetime
) -> dict:
    return await repo.get_week_stats(db, user.id, week_start)


async def get_personal_records(db: AsyncSession, user: User) -> list:
    return await repo.get_personal_records(db, user.id)

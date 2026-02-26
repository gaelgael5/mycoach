"""Service de progression automatique des charges — B4-08.

Règle : si l'utilisateur atteint les reps cibles sur 3 séances consécutives
→ on augmente le target_weight_kg de 2.5 kg (ou 5% si pas de poids défini).
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise_set import ExerciseSet
from app.models.performance_session import PerformanceSession
from app.models.workout_plan import PlannedExercise, PlannedSession, WorkoutPlan, PlanAssignment


CONSECUTIVE_SESSIONS_REQUIRED = 3
DEFAULT_INCREMENT_KG = Decimal("2.5")


async def check_and_adjust(
    db: AsyncSession, client_id: uuid.UUID, exercise_type_id: uuid.UUID
) -> PlannedExercise | None:
    """Analyse les dernières séances et ajuste target_weight_kg si règle atteinte.

    Retourne l'exercice planifié modifié, ou None si pas d'ajustement.
    """
    # 1. Récupérer le plan actif du client
    q = (
        select(PlanAssignment)
        .where(PlanAssignment.client_id == client_id, PlanAssignment.active.is_(True))
        .order_by(PlanAssignment.created_at.desc())
        .limit(1)
    )
    assignment = (await db.execute(q)).scalar_one_or_none()
    if assignment is None:
        return None

    # 2. Trouver l'exercice planifié correspondant
    q = (
        select(PlannedExercise)
        .join(PlannedSession, PlannedExercise.planned_session_id == PlannedSession.id)
        .where(
            PlannedSession.plan_id == assignment.plan_id,
            PlannedExercise.exercise_type_id == exercise_type_id,
        )
        .limit(1)
    )
    planned = (await db.execute(q)).scalar_one_or_none()
    if planned is None:
        return None

    # 3. Récupérer les N dernières séances avec cet exercice
    q = (
        select(ExerciseSet)
        .join(PerformanceSession, ExerciseSet.session_id == PerformanceSession.id)
        .where(
            PerformanceSession.user_id == client_id,
            ExerciseSet.exercise_type_id == exercise_type_id,
        )
        .order_by(PerformanceSession.session_date.desc())
        .limit(CONSECUTIVE_SESSIONS_REQUIRED)
    )
    last_sets = (await db.execute(q)).scalars().all()

    if len(last_sets) < CONSECUTIVE_SESSIONS_REQUIRED:
        return None  # Pas assez de données

    # 4. Vérifier que les reps cibles sont atteintes sur chaque séance
    target_reps = planned.target_reps
    all_reached = all(
        (s.reps or 0) >= target_reps for s in last_sets
    )
    if not all_reached:
        return None

    # 5. Augmenter la charge
    current = planned.target_weight_kg or Decimal("0")
    if current > 0:
        planned.target_weight_kg = current + DEFAULT_INCREMENT_KG
    else:
        # Pas encore de poids cible défini → mettre 5kg par défaut
        planned.target_weight_kg = Decimal("5.0")

    await db.flush()

    # TODO B2-17 : notifier le client de l'augmentation de charge
    return planned

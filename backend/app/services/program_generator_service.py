"""Générateur de programmes d'entraînement (règles métier) — B4-07.

Génère un programme hebdomadaire adapté au questionnaire du client.
Règles :
- Distribution musculaire équilibrée (pas 2 jours consécutifs sur le même groupe)
- Alternance push/pull
- Repos minimum 1 jour entre 2 séances d'intensité élevée
- Adaptation au niveau et à l'objectif
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.exercise_type import ExerciseType, ExerciseTypeMuscle
from app.models.workout_plan import WorkoutPlan, PlannedSession, PlannedExercise


# ── Templates de programmes ────────────────────────────────────────────────────

@dataclass
class SessionTemplate:
    name: str
    day_of_week: int  # 0=Lundi
    muscle_focus: list[str]  # groupes primaires ciblés
    estimated_duration_min: int
    rest_seconds: int
    # (category_filter, sets, reps, note)
    exercises: list[tuple[str, int, int]]


# Programmes selon fréquence et objectif
PROGRAMS: dict[str, list[SessionTemplate]] = {
    # Perte de poids (cardio + full body)
    "lose_weight_3": [
        SessionTemplate("Full Body A", 0, ["full_body", "quads", "chest"], 50, 60,
                        [("strength", 3, 12), ("cardio", 1, 20), ("core", 3, 15)]),
        SessionTemplate("Cardio + Core", 2, ["full_body", "core"], 40, 60,
                        [("cardio", 1, 30), ("core", 3, 20), ("hiit", 2, 15)]),
        SessionTemplate("Full Body B", 4, ["full_body", "back", "glutes"], 50, 60,
                        [("strength", 3, 12), ("cardio", 1, 20), ("core", 3, 15)]),
    ],
    # Prise de muscle (split push/pull/legs)
    "muscle_gain_3": [
        SessionTemplate("Push (Poitrine + Épaules + Triceps)", 0,
                        ["chest", "shoulders", "triceps"], 60, 90,
                        [("strength", 4, 8), ("strength", 3, 10), ("strength", 3, 12)]),
        SessionTemplate("Pull (Dos + Biceps)", 2, ["back", "biceps"], 60, 90,
                        [("strength", 4, 8), ("strength", 3, 10), ("strength", 3, 12)]),
        SessionTemplate("Legs (Jambes + Fessiers)", 4, ["quads", "hamstrings", "glutes"], 60, 90,
                        [("strength", 4, 8), ("strength", 3, 10), ("strength", 3, 12)]),
    ],
    "muscle_gain_4": [
        SessionTemplate("Push A (Poitrine + Épaules)", 0, ["chest", "shoulders"], 60, 90,
                        [("strength", 4, 8), ("strength", 3, 10), ("strength", 3, 12)]),
        SessionTemplate("Pull A (Dos + Biceps)", 1, ["back", "biceps"], 60, 90,
                        [("strength", 4, 8), ("strength", 3, 10), ("strength", 3, 12)]),
        SessionTemplate("Legs", 3, ["quads", "hamstrings", "glutes"], 60, 90,
                        [("strength", 4, 8), ("strength", 3, 10), ("strength", 3, 12)]),
        SessionTemplate("Push B (Épaules + Triceps)", 5, ["shoulders", "triceps"], 55, 90,
                        [("strength", 4, 10), ("strength", 3, 12), ("strength", 3, 15)]),
    ],
    # Bien-être / maintenance
    "well_being_3": [
        SessionTemplate("Yoga + Core", 0, ["core", "full_body"], 45, 30,
                        [("yoga", 1, 10), ("core", 3, 15), ("flexibility", 2, 20)]),
        SessionTemplate("Cardio léger", 2, ["full_body"], 40, 30,
                        [("cardio", 1, 30), ("flexibility", 2, 20), ("core", 2, 15)]),
        SessionTemplate("Renforcement global", 4, ["full_body"], 50, 60,
                        [("strength", 3, 12), ("core", 3, 15), ("yoga", 1, 15)]),
    ],
    # Endurance
    "endurance_3": [
        SessionTemplate("Cardio Long", 0, ["full_body"], 60, 30,
                        [("cardio", 1, 45), ("core", 2, 20)]),
        SessionTemplate("Fractionné", 2, ["full_body"], 45, 45,
                        [("hiit", 4, 10), ("cardio", 1, 15), ("core", 2, 15)]),
        SessionTemplate("Endurance + Renforcement", 4, ["full_body", "quads"], 55, 45,
                        [("cardio", 1, 30), ("strength", 3, 15), ("core", 2, 15)]),
    ],
}


async def generate_weekly_program(
    db: AsyncSession,
    *,
    goal: str,
    frequency_per_week: int,
    level: str,
    client_id: uuid.UUID | None = None,
) -> WorkoutPlan:
    """Génère un programme hebdomadaire en IA pure (règles métier).

    Crée le plan + sessions + exercices en base.
    """
    # Choisir le template
    key = f"{goal}_{frequency_per_week}"
    if key not in PROGRAMS:
        # Fallback au plus proche
        fallback_keys = [k for k in PROGRAMS if k.startswith(goal)]
        if fallback_keys:
            key = fallback_keys[0]
        else:
            key = "well_being_3"

    templates = PROGRAMS[key]

    # Créer le plan
    plan = WorkoutPlan(
        id=uuid.uuid4(),
        name=_plan_name(goal, level),
        description=_plan_description(goal, level, frequency_per_week),
        duration_weeks=4,
        level=level,
        goal=goal,
        created_by_id=None,  # IA : pas de fake user
        is_ai_generated=True,
        archived=False,
    )
    db.add(plan)
    await db.flush()

    # Créer les sessions planifiées
    for idx, tpl in enumerate(templates):
        ps = PlannedSession(
            id=uuid.uuid4(),
            plan_id=plan.id,
            day_of_week=tpl.day_of_week,
            session_name=tpl.name,
            estimated_duration_min=tpl.estimated_duration_min,
            rest_seconds=tpl.rest_seconds,
            order_index=idx + 1,
        )
        db.add(ps)
        await db.flush()

        # Ajouter des exercices selon les muscles cibles
        exercises = await _pick_exercises(db, tpl, level)
        for ex_idx, (ex_type, target_sets, target_reps) in enumerate(exercises):
            pe = PlannedExercise(
                id=uuid.uuid4(),
                planned_session_id=ps.id,
                exercise_type_id=ex_type.id,
                target_sets=target_sets,
                target_reps=target_reps,
                target_weight_kg=None,  # ajusté automatiquement après premières séances
                order_index=ex_idx + 1,
            )
            db.add(pe)

    await db.flush()
    return plan


async def _pick_exercises(
    db: AsyncSession,
    template: SessionTemplate,
    level: str,
) -> list[tuple[ExerciseType, int, int]]:
    """Sélectionne les exercices correspondant aux muscles et catégories cibles."""
    result = []
    for category, sets, reps in template.exercises:
        # Chercher des exercices dans la catégorie ET dans les muscles cibles
        q = (
            select(ExerciseType)
            .join(ExerciseTypeMuscle, ExerciseTypeMuscle.exercise_type_id == ExerciseType.id)
            .where(
                ExerciseType.category == category,
                ExerciseType.difficulty == level,
                ExerciseType.active.is_(True),
                ExerciseTypeMuscle.muscle_group.in_(template.muscle_focus),
                ExerciseTypeMuscle.role == "primary",
            )
            .limit(1)
        )
        ex = (await db.execute(q)).scalar_one_or_none()
        if ex is None:
            # Fallback : même catégorie sans contrainte muscle
            q2 = (
                select(ExerciseType)
                .where(
                    ExerciseType.category == category,
                    ExerciseType.active.is_(True),
                )
                .limit(1)
            )
            ex = (await db.execute(q2)).scalar_one_or_none()
        if ex:
            result.append((ex, sets, reps))
    return result


def _plan_name(goal: str, level: str) -> str:
    labels = {
        "lose_weight": "Programme Perte de Poids",
        "muscle_gain": "Programme Prise de Masse",
        "endurance": "Programme Endurance",
        "well_being": "Programme Bien-être",
        "maintenance": "Programme Maintenance",
        "rehab": "Programme Rééducation",
    }
    levels = {"beginner": "Débutant", "intermediate": "Intermédiaire", "advanced": "Avancé"}
    return f"{labels.get(goal, 'Programme')} — {levels.get(level, level)}"


def _plan_description(goal: str, level: str, freq: int) -> str:
    return (
        f"Programme généré automatiquement pour objectif {goal}, "
        f"niveau {level}, {freq} séances/semaine."
    )

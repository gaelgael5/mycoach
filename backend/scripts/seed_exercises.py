#!/usr/bin/env python3
"""Seed — 55 exercices de base avec groupes musculaires — B3-08.

Usage:
    python scripts/seed_exercises.py [--dry-run]
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncpg


# ── Données : (name_key, category, difficulty, primary_muscles, secondary_muscles) ──

EXERCISES = [
    # ── Poitrine ───────────────────────────────────────────────────────────────
    ("exercise.bench_press_flat", "strength", "intermediate",
     ["chest"], ["triceps", "shoulders"]),
    ("exercise.bench_press_incline", "strength", "intermediate",
     ["chest"], ["shoulders", "triceps"]),
    ("exercise.bench_press_decline", "strength", "advanced",
     ["chest"], ["triceps"]),
    ("exercise.dumbbell_fly", "strength", "intermediate",
     ["chest"], ["shoulders"]),
    ("exercise.push_up", "strength", "beginner",
     ["chest"], ["triceps", "shoulders", "core"]),
    ("exercise.cable_fly", "strength", "intermediate",
     ["chest"], ["triceps"]),

    # ── Dos ────────────────────────────────────────────────────────────────────
    ("exercise.pull_up", "strength", "intermediate",
     ["back"], ["biceps", "forearms"]),
    ("exercise.lat_pulldown", "strength", "beginner",
     ["back"], ["biceps", "forearms"]),
    ("exercise.seated_row", "strength", "beginner",
     ["back"], ["biceps", "forearms"]),
    ("exercise.bent_over_row", "strength", "intermediate",
     ["back"], ["biceps", "core"]),
    ("exercise.deadlift", "strength", "advanced",
     ["back"], ["glutes", "hamstrings", "core"]),
    ("exercise.face_pull", "strength", "beginner",
     ["back"], ["shoulders"]),

    # ── Épaules ────────────────────────────────────────────────────────────────
    ("exercise.overhead_press", "strength", "intermediate",
     ["shoulders"], ["triceps", "core"]),
    ("exercise.lateral_raise", "strength", "beginner",
     ["shoulders"], []),
    ("exercise.front_raise", "strength", "beginner",
     ["shoulders"], []),
    ("exercise.arnold_press", "strength", "intermediate",
     ["shoulders"], ["triceps"]),
    ("exercise.shrug", "strength", "beginner",
     ["shoulders"], ["neck"]),

    # ── Biceps ─────────────────────────────────────────────────────────────────
    ("exercise.barbell_curl", "strength", "beginner",
     ["biceps"], ["forearms"]),
    ("exercise.dumbbell_curl", "strength", "beginner",
     ["biceps"], ["forearms"]),
    ("exercise.hammer_curl", "strength", "beginner",
     ["biceps"], ["forearms"]),
    ("exercise.preacher_curl", "strength", "intermediate",
     ["biceps"], []),
    ("exercise.concentration_curl", "strength", "beginner",
     ["biceps"], []),

    # ── Triceps ────────────────────────────────────────────────────────────────
    ("exercise.tricep_dip", "strength", "intermediate",
     ["triceps"], ["chest", "shoulders"]),
    ("exercise.skull_crusher", "strength", "intermediate",
     ["triceps"], []),
    ("exercise.cable_pushdown", "strength", "beginner",
     ["triceps"], []),
    ("exercise.overhead_tricep_extension", "strength", "beginner",
     ["triceps"], []),

    # ── Jambes ─────────────────────────────────────────────────────────────────
    ("exercise.squat", "strength", "intermediate",
     ["quads"], ["glutes", "hamstrings", "core"]),
    ("exercise.front_squat", "strength", "advanced",
     ["quads"], ["glutes", "core"]),
    ("exercise.leg_press", "strength", "beginner",
     ["quads"], ["glutes", "hamstrings"]),
    ("exercise.lunge", "strength", "beginner",
     ["quads"], ["glutes", "hamstrings"]),
    ("exercise.bulgarian_split_squat", "strength", "intermediate",
     ["quads"], ["glutes", "hamstrings"]),
    ("exercise.leg_extension", "strength", "beginner",
     ["quads"], []),
    ("exercise.leg_curl", "strength", "beginner",
     ["hamstrings"], ["glutes"]),
    ("exercise.romanian_deadlift", "strength", "intermediate",
     ["hamstrings"], ["glutes", "back"]),
    ("exercise.hip_thrust", "strength", "intermediate",
     ["glutes"], ["hamstrings"]),
    ("exercise.calf_raise", "strength", "beginner",
     ["calves"], []),

    # ── Core ───────────────────────────────────────────────────────────────────
    ("exercise.plank", "strength", "beginner",
     ["core"], ["shoulders"]),
    ("exercise.crunch", "strength", "beginner",
     ["core"], []),
    ("exercise.leg_raise", "strength", "beginner",
     ["core"], ["hip_flexors"]),
    ("exercise.russian_twist", "strength", "beginner",
     ["core"], []),
    ("exercise.ab_wheel", "strength", "advanced",
     ["core"], ["shoulders", "back"]),
    ("exercise.cable_crunch", "strength", "intermediate",
     ["core"], []),

    # ── Cardio ─────────────────────────────────────────────────────────────────
    ("exercise.running", "cardio", "beginner",
     ["full_body"], ["calves", "quads"]),
    ("exercise.cycling", "cardio", "beginner",
     ["quads"], ["hamstrings", "calves"]),
    ("exercise.rowing_machine", "cardio", "intermediate",
     ["back"], ["quads", "core"]),
    ("exercise.jump_rope", "cardio", "beginner",
     ["calves"], ["shoulders", "core"]),
    ("exercise.burpee", "hiit", "intermediate",
     ["full_body"], ["chest", "shoulders", "quads"]),

    # ── Flexibilité / Bien-être ────────────────────────────────────────────────
    ("exercise.yoga_sun_salutation", "yoga", "beginner",
     ["full_body"], []),
    ("exercise.yoga_warrior", "yoga", "beginner",
     ["quads"], ["core", "shoulders"]),
    ("exercise.foam_roll_back", "rehab", "beginner",
     ["back"], []),
    ("exercise.hip_flexor_stretch", "flexibility", "beginner",
     ["hip_flexors"], []),
    ("exercise.hamstring_stretch", "flexibility", "beginner",
     ["hamstrings"], []),
    ("exercise.shoulder_stretch", "flexibility", "beginner",
     ["shoulders"], []),
    ("exercise.chest_stretch", "flexibility", "beginner",
     ["chest"], []),
    ("exercise.pigeon_pose", "yoga", "intermediate",
     ["glutes"], ["hip_flexors"]),
    ("exercise.cat_cow", "rehab", "beginner",
     ["back"], ["core"]),
]


async def seed(dry_run: bool = False) -> None:
    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://mycoach:mycoach_test@localhost:5432/mycoach_test",
    ).replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(db_url)
    inserted = 0
    skipped = 0

    try:
        for name_key, category, difficulty, primary_muscles, secondary_muscles in EXERCISES:
            # Upsert exercise type
            existing = await conn.fetchrow(
                "SELECT id FROM exercise_types WHERE name_key = $1", name_key
            )
            if existing:
                et_id = existing["id"]
                skipped += 1
            else:
                import uuid as _uuid
                et_id = _uuid.uuid4()
                if not dry_run:
                    await conn.execute(
                        """
                        INSERT INTO exercise_types (id, name_key, category, difficulty, active)
                        VALUES ($1, $2, $3, $4, TRUE)
                        """,
                        et_id, name_key, category, difficulty,
                    )
                    # Insert muscles
                    for muscle in primary_muscles:
                        await conn.execute(
                            """
                            INSERT INTO exercise_type_muscles (id, exercise_type_id, muscle_group, role)
                            VALUES ($1, $2, $3, 'primary')
                            """,
                            _uuid.uuid4(), et_id, muscle,
                        )
                    for muscle in secondary_muscles:
                        await conn.execute(
                            """
                            INSERT INTO exercise_type_muscles (id, exercise_type_id, muscle_group, role)
                            VALUES ($1, $2, $3, 'secondary')
                            """,
                            _uuid.uuid4(), et_id, muscle,
                        )
                inserted += 1

        print(f"{'[DRY-RUN] ' if dry_run else ''}Exercices : {inserted} insérés, {skipped} déjà présents")
    finally:
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    asyncio.run(seed(dry_run=args.dry_run))

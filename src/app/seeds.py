"""Seed data for MyCoach."""
import asyncio
from app.db.base import async_session, engine, Base
from app.models.tables import *  # noqa


BASE_EXERCISES = [
    {"name": "Squat", "sets": 4, "reps": "8-10", "rest_seconds": 120},
    {"name": "Bench Press", "sets": 4, "reps": "8-10", "rest_seconds": 120},
    {"name": "Deadlift", "sets": 3, "reps": "5", "rest_seconds": 180},
    {"name": "Overhead Press", "sets": 4, "reps": "8-10", "rest_seconds": 90},
    {"name": "Barbell Row", "sets": 4, "reps": "8-10", "rest_seconds": 90},
    {"name": "Pull-Up", "sets": 3, "reps": "8-12", "rest_seconds": 90},
    {"name": "Lunges", "sets": 3, "reps": "12", "rest_seconds": 60},
    {"name": "Plank", "sets": 3, "reps": "60s", "rest_seconds": 60},
    {"name": "Dumbbell Curl", "sets": 3, "reps": "12", "rest_seconds": 60},
    {"name": "Triceps Dip", "sets": 3, "reps": "10-12", "rest_seconds": 60},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print(f"Seed data: {len(BASE_EXERCISES)} base exercises available.")
    print("Base exercises (for reference when creating programs):")
    for ex in BASE_EXERCISES:
        print(f"  - {ex['name']}: {ex['sets']}x{ex['reps']} (rest: {ex['rest_seconds']}s)")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())

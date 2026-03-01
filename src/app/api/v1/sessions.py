"""Sessions & Exercises endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.tables import ProgramSession, Exercise, Program, Coach
from app.api.deps import get_current_coach
from app.schemas.program import (
    SessionUpdate, SessionReadBrief,
    ExerciseCreate, ExerciseUpdate, ExerciseRead,
)

router = APIRouter(tags=["sessions-exercises"])


async def _get_session_for_coach(session_id: uuid.UUID, coach: Coach, db: AsyncSession) -> ProgramSession:
    result = await db.execute(
        select(ProgramSession).join(Program).where(
            ProgramSession.id == session_id, Program.coach_id == coach.id
        )
    )
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess


@router.patch("/sessions/{session_id}", response_model=SessionReadBrief)
async def update_session(
    session_id: uuid.UUID,
    body: SessionUpdate,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    sess = await _get_session_for_coach(session_id, coach, db)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(sess, k, v)
    await db.flush()
    await db.refresh(sess)
    return sess


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: uuid.UUID,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    sess = await _get_session_for_coach(session_id, coach, db)
    await db.delete(sess)


@router.post("/sessions/{session_id}/exercises", response_model=ExerciseRead, status_code=201)
async def create_exercise(
    session_id: uuid.UUID,
    body: ExerciseCreate,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    await _get_session_for_coach(session_id, coach, db)
    ex = Exercise(session_id=session_id, **body.model_dump())
    db.add(ex)
    await db.flush()
    await db.refresh(ex)
    return ex


async def _get_exercise_for_coach(exercise_id: uuid.UUID, coach: Coach, db: AsyncSession) -> Exercise:
    result = await db.execute(
        select(Exercise)
        .join(ProgramSession)
        .join(Program)
        .where(Exercise.id == exercise_id, Program.coach_id == coach.id)
    )
    ex = result.scalar_one_or_none()
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return ex


@router.patch("/exercises/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
    exercise_id: uuid.UUID,
    body: ExerciseUpdate,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    ex = await _get_exercise_for_coach(exercise_id, coach, db)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(ex, k, v)
    await db.flush()
    await db.refresh(ex)
    return ex


@router.delete("/exercises/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: uuid.UUID,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    ex = await _get_exercise_for_coach(exercise_id, coach, db)
    await db.delete(ex)

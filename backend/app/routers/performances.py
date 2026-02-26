"""Router performances — B3-12."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user, require_coach
from app.database import get_db
from app.models.user import User
from app.repositories import performance_repository as repo
from app.schemas.performance import (
    PerformanceSessionCreate,
    PerformanceSessionResponse,
    PerformanceSessionUpdate,
    ProgressionStats,
    WeekStats,
    PersonalRecordResponse,
)
from app.schemas.common import MessageResponse
from app.services import performance_service
from app.services.performance_service import (
    SessionNotFoundError, NotAuthorizedError, EditWindowExpiredError
)

router = APIRouter(prefix="/performances", tags=["performances"])


def _perf_err(e: Exception) -> HTTPException:
    if isinstance(e, SessionNotFoundError):
        return HTTPException(status_code=404, detail=str(e))
    if isinstance(e, NotAuthorizedError):
        return HTTPException(status_code=403, detail=str(e))
    if isinstance(e, EditWindowExpiredError):
        return HTTPException(status_code=422, detail=str(e))
    return HTTPException(status_code=500, detail=str(e))


# ── CRUD sessions ──────────────────────────────────────────────────────────────

@router.post("", response_model=PerformanceSessionResponse, status_code=201)
async def create_session(
    data: PerformanceSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await performance_service.create_session(db, current_user, data)
    await db.commit()
    return await repo.get_by_id(db, session.id)


@router.post("/for-client/{client_id}", response_model=PerformanceSessionResponse, status_code=201)
async def create_session_for_client(
    client_id: uuid.UUID,
    data: PerformanceSessionCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    """Coach saisit les performances pour un client (session_type=coached)."""
    from app.models.user import User as UserModel
    from sqlalchemy import select
    q = select(UserModel).where(UserModel.id == client_id)
    client = (await db.execute(q)).scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=404, detail="Client introuvable")
    session = await performance_service.create_session(
        db, client, data, entered_by_id=current_user.id
    )
    await db.commit()
    return await repo.get_by_id(db, session.id)


@router.get("", response_model=dict)
async def list_sessions(
    session_type: str | None = Query(None),
    gym_id: uuid.UUID | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await performance_service.get_history(
        db, current_user,
        session_type=session_type, gym_id=gym_id,
        from_date=from_date, to_date=to_date,
        offset=offset, limit=limit,
    )
    return {
        "items": [PerformanceSessionResponse.model_validate(s) for s in items],
        "total": total, "offset": offset, "limit": limit,
    }


@router.get("/personal-records", response_model=list[PersonalRecordResponse])
async def get_personal_records(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await performance_service.get_personal_records(db, current_user)


@router.get("/stats/week", response_model=WeekStats)
async def get_week_stats(
    week_start: datetime = Query(..., description="Lundi de la semaine (UTC)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stats = await performance_service.get_week_dashboard(db, current_user, week_start)
    return WeekStats(**stats)


@router.get("/stats/exercise/{exercise_type_id}", response_model=ProgressionStats)
async def get_exercise_progression(
    exercise_type_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories.performance_repository import get_exercise_by_id
    exercise = await get_exercise_by_id(db, exercise_type_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    data_points = await performance_service.get_progression(db, current_user, exercise_type_id)
    return ProgressionStats(
        exercise_type_id=exercise_type_id,
        exercise_name_key=exercise.name_key,
        data_points=data_points,
    )


@router.put("/{session_id}", response_model=PerformanceSessionResponse)
async def update_session(
    session_id: uuid.UUID,
    data: PerformanceSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        session = await performance_service.update_session(db, current_user, session_id, data)
        await db.commit()
        return session
    except Exception as e:
        raise _perf_err(e)


@router.delete("/{session_id}", response_model=MessageResponse)
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await performance_service.delete_session(db, current_user, session_id)
        await db.commit()
        return {"message": "Session supprimée"}
    except Exception as e:
        raise _perf_err(e)

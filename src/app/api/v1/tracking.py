"""Tracking endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.tables import SessionLog, Metric, Client, ProgramSession, Program, Coach
from app.api.deps import get_current_coach
from app.schemas.tracking import (
    SessionLogCreate, SessionLogRead, MetricCreate, MetricRead, DashboardResponse,
)

router = APIRouter(prefix="/tracking", tags=["tracking"])


async def _verify_client(client_id: uuid.UUID, coach: Coach, db: AsyncSession) -> Client:
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.coach_id == coach.id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("/sessions/{session_id}/log", response_model=SessionLogRead, status_code=201)
async def log_session(
    session_id: uuid.UUID,
    body: SessionLogCreate,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProgramSession).join(Program).where(
            ProgramSession.id == session_id, Program.coach_id == coach.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")
    await _verify_client(body.client_id, coach, db)
    log = SessionLog(session_id=session_id, **body.model_dump())
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


@router.get("/clients/{client_id}/logs", response_model=list[SessionLogRead])
async def get_client_logs(
    client_id: uuid.UUID,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    await _verify_client(client_id, coach, db)
    result = await db.execute(
        select(SessionLog).where(SessionLog.client_id == client_id).order_by(SessionLog.logged_at.desc())
    )
    return result.scalars().all()


@router.post("/metrics", response_model=MetricRead, status_code=201)
async def create_metric(
    body: MetricCreate,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    await _verify_client(body.client_id, coach, db)
    metric = Metric(**body.model_dump())
    db.add(metric)
    await db.flush()
    await db.refresh(metric)
    return metric


@router.get("/clients/{client_id}/metrics", response_model=list[MetricRead])
async def get_client_metrics(
    client_id: uuid.UUID,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    await _verify_client(client_id, coach, db)
    result = await db.execute(
        select(Metric).where(Metric.client_id == client_id).order_by(Metric.date.desc())
    )
    return result.scalars().all()


@router.get("/clients/{client_id}/dashboard", response_model=DashboardResponse)
async def get_client_dashboard(
    client_id: uuid.UUID,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    await _verify_client(client_id, coach, db)

    total_q = await db.execute(
        select(func.count(SessionLog.id)).where(SessionLog.client_id == client_id)
    )
    total = total_q.scalar() or 0

    completed_q = await db.execute(
        select(func.count(SessionLog.id)).where(
            SessionLog.client_id == client_id, SessionLog.completed == True  # noqa
        )
    )
    completed = completed_q.scalar() or 0

    types_q = await db.execute(
        select(distinct(Metric.metric_type)).where(Metric.client_id == client_id)
    )
    metric_types = types_q.scalars().all()

    latest_metrics = {}
    for mt in metric_types:
        latest_q = await db.execute(
            select(Metric).where(Metric.client_id == client_id, Metric.metric_type == mt)
            .order_by(Metric.date.desc()).limit(1)
        )
        m = latest_q.scalar_one_or_none()
        if m:
            latest_metrics[mt] = m.value

    return DashboardResponse(
        total_sessions_logged=total,
        completed_sessions=completed,
        completion_rate=round(completed / total, 2) if total > 0 else 0.0,
        latest_metrics=latest_metrics,
    )

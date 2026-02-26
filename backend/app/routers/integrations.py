"""Router intégrations OAuth — Strava, Google Calendar, Withings — B5-07."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.repositories import integration_repository as repo
from app.schemas.integration import (
    AuthorizeResponse, BodyMeasurementCreate, BodyMeasurementResponse,
    ConnectResponse, IntegrationStatus, StravaActivityResponse,
)
from app.services import strava_service, calendar_service, scale_service

router = APIRouter(prefix="/integrations", tags=["integrations"])


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


# ── Statut global ──────────────────────────────────────────────────────────────

@router.get("/status", response_model=list[IntegrationStatus])
async def get_integration_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les intégrations connectées de l'utilisateur."""
    tokens = await repo.list_user_tokens(db, current_user.id)
    token_map = {t.provider: t for t in tokens}
    providers = ["strava", "google_calendar", "withings"]
    return [
        IntegrationStatus(
            provider=p,
            connected=p in token_map,
            scope=token_map[p].scope if p in token_map else None,
            expires_at=token_map[p].expires_at if p in token_map else None,
        )
        for p in providers
    ]


@router.delete("/disconnect/{provider}", response_model=dict)
async def disconnect(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await repo.delete_token(db, current_user.id, provider)
    await db.commit()
    if not deleted:
        raise HTTPException(status_code=404, detail="Intégration non trouvée")
    return {"message": f"{provider} déconnecté"}


# ── Strava ─────────────────────────────────────────────────────────────────────

@router.get("/strava", response_model=AuthorizeResponse)
async def strava_authorize(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    url = strava_service.build_authorize_url(
        state=str(current_user.id), base_url=_base_url(request)
    )
    return AuthorizeResponse(authorize_url=url, provider="strava")


@router.get("/strava/callback", response_model=ConnectResponse)
async def strava_callback(
    code: str = Query(...),
    state: str = Query(""),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await strava_service.handle_callback(
        db, current_user.id, code, base_url=_base_url(request)
    )
    return ConnectResponse(status=result["status"], provider="strava", scope=result.get("scope"))


@router.post("/strava/push/{session_id}", response_model=StravaActivityResponse)
async def push_strava(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.performance_session import PerformanceSession
    from sqlalchemy import select
    q = select(PerformanceSession).where(
        PerformanceSession.id == session_id,
        PerformanceSession.user_id == current_user.id,
    )
    session = (await db.execute(q)).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Séance introuvable")
    try:
        result = await strava_service.push_session(db, current_user.id, session)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return StravaActivityResponse(**result, status="pushed")


@router.get("/strava/import", response_model=list[dict])
async def import_strava(
    per_page: int = Query(10, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        activities = await strava_service.import_activities(
            db, current_user.id, per_page=per_page
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return activities


# ── Google Calendar ────────────────────────────────────────────────────────────

@router.get("/calendar", response_model=AuthorizeResponse)
async def calendar_authorize(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    url = calendar_service.build_authorize_url(
        state=str(current_user.id), base_url=_base_url(request)
    )
    return AuthorizeResponse(authorize_url=url, provider="google_calendar")


@router.get("/calendar/callback", response_model=ConnectResponse)
async def calendar_callback(
    code: str = Query(...),
    state: str = Query(""),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await calendar_service.handle_callback(
        db, current_user.id, code, base_url=_base_url(request)
    )
    return ConnectResponse(
        status=result["status"], provider="google_calendar", scope=result.get("scope")
    )


@router.post("/calendar/sync/{booking_id}", response_model=dict)
async def sync_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.booking import Booking
    from sqlalchemy import select
    q = select(Booking).where(Booking.id == booking_id)
    booking = (await db.execute(q)).scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=404, detail="Réservation introuvable")
    try:
        event = await calendar_service.sync_booking(db, current_user.id, booking)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"status": "synced", "event_id": event.get("id")}


# ── Balance (Withings) ─────────────────────────────────────────────────────────

@router.get("/scale", response_model=AuthorizeResponse)
async def scale_authorize(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    url = scale_service.build_authorize_url(
        state=str(current_user.id), base_url=_base_url(request)
    )
    return AuthorizeResponse(authorize_url=url, provider="withings")


@router.get("/scale/callback", response_model=ConnectResponse)
async def scale_callback(
    code: str = Query(...),
    state: str = Query(""),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await scale_service.handle_callback(
        db, current_user.id, code, base_url=_base_url(request)
    )
    return ConnectResponse(
        status=result["status"], provider="withings", scope=result.get("scope")
    )


@router.get("/scale/import", response_model=list[BodyMeasurementResponse])
async def import_scale(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        measurements = await scale_service.import_measurements(db, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return [BodyMeasurementResponse.model_validate(m) for m in measurements]


@router.post("/scale/manual", response_model=BodyMeasurementResponse, status_code=201)
async def manual_scale(
    data: BodyMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    m = await scale_service.manual_entry(
        db,
        current_user.id,
        measured_at=data.measured_at,
        weight_kg=data.weight_kg,
        fat_pct=data.fat_pct,
        muscle_pct=data.muscle_pct,
        bone_kg=data.bone_kg,
        water_pct=data.water_pct,
        bmi=data.bmi,
    )
    return BodyMeasurementResponse.model_validate(m)


@router.get("/scale/history", response_model=list[BodyMeasurementResponse])
async def scale_history(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    measurements = await repo.list_measurements(
        db, current_user.id, limit=limit, offset=offset
    )
    return [BodyMeasurementResponse.model_validate(m) for m in measurements]

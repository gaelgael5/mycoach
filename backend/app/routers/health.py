"""Router — Paramètres de santé, logs, partage."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user, require_coach
from app.database import get_db
from app.models.user import User
from app.schemas.health import (
    HealthLogCreate,
    HealthLogResponse,
    HealthParameterResponse,
    HealthSharingResponse,
    HealthSharingUpdate,
)
from app.services import health_service
from app.services.health_service import LogNotFoundError

router = APIRouter(prefix="/health", tags=["health"])


# ---------------------------------------------------------------------------
# Paramètres de santé (lecture)
# ---------------------------------------------------------------------------

@router.get("/parameters", response_model=list[HealthParameterResponse])
async def list_parameters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les paramètres de santé actifs."""
    return await health_service.get_active_parameters(db)


# ---------------------------------------------------------------------------
# Logs de mesures
# ---------------------------------------------------------------------------

@router.post("/logs", response_model=HealthLogResponse, status_code=201)
async def log_measurement(
    data: HealthLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enregistrer une nouvelle mesure de santé."""
    log = await health_service.log_measurement(db, current_user.id, data)
    await db.commit()
    # Refresh with relationships
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.health_log import HealthLog
    q = select(HealthLog).where(HealthLog.id == log.id).options(selectinload(HealthLog.parameter))
    from sqlalchemy.ext.asyncio import AsyncSession as _AS
    result = (await db.execute(q)).scalar_one()
    return result


@router.get("/logs", response_model=list[HealthLogResponse])
async def get_my_logs(
    parameter_id: Optional[uuid.UUID] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mon historique de mesures (avec filtres optionnels)."""
    return await health_service.get_my_logs(db, current_user.id, parameter_id, from_date, to_date)


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Supprimer une mesure (propriétaire uniquement)."""
    try:
        await health_service.delete_log(db, current_user.id, log_id)
        await db.commit()
    except LogNotFoundError:
        raise HTTPException(status_code=404, detail="Mesure introuvable")


# ---------------------------------------------------------------------------
# Préférences de partage
# ---------------------------------------------------------------------------

@router.get("/sharing/{coach_id}", response_model=list[HealthSharingResponse])
async def get_sharing(
    coach_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mes préférences de partage avec un coach spécifique."""
    items = await health_service.get_my_sharing(db, current_user.id, coach_id)
    return [HealthSharingResponse(**item) for item in items]


@router.patch("/sharing/{coach_id}", response_model=list[HealthSharingResponse])
async def update_sharing(
    coach_id: uuid.UUID,
    data: HealthSharingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mettre à jour les préférences de partage."""
    settings = await health_service.update_sharing(db, current_user.id, coach_id, data.updates)
    await db.commit()
    return [
        HealthSharingResponse(parameter_id=s.parameter_id, shared=s.shared)
        for s in settings
    ]


# ---------------------------------------------------------------------------
# Coach — mesures d'un client (filtrées par partage)
# ---------------------------------------------------------------------------

@router.get("/clients/{client_id}/logs", response_model=list[HealthLogResponse])
async def get_client_logs(
    client_id: uuid.UUID,
    parameter_id: Optional[uuid.UUID] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    """Mesures partagées d'un client (coach seulement)."""
    return await health_service.get_client_logs(
        db, current_user.id, client_id, parameter_id, from_date, to_date
    )

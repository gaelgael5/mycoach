"""Router paiements & forfaits — B1-27."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_coach
from app.database import get_db
from app.models.user import User
from app.repositories import payment_repository
from app.schemas.payment import (
    PackageCreate, PackageResponse,
    PaymentRecord, PaymentResponse,
    HoursSummary,
)
from app.services import payment_service
from app.services.payment_service import PackageNotFoundError, PackageExhaustedError

router = APIRouter(prefix="/coaches/clients", tags=["payments"])


# ── Forfaits ──────────────────────────────────────────────────────────────────

@router.post("/{client_id}/packages", response_model=PackageResponse, status_code=201)
async def create_package(
    client_id: uuid.UUID,
    data: PackageCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    pkg = await payment_service.create_package_for_client(db, current_user, client_id, data)
    await db.commit()
    return pkg


@router.get("/{client_id}/packages", response_model=list[PackageResponse])
async def list_packages(
    client_id: uuid.UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    return await payment_repository.get_history(
        db, client_id, current_user.id, offset=offset, limit=limit
    )


# ── Paiements ──────────────────────────────────────────────────────────────────

@router.post("/{client_id}/payments", response_model=PaymentResponse, status_code=201)
async def record_payment(
    client_id: uuid.UUID,
    data: PaymentRecord,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    pmt = await payment_service.record_payment(db, current_user, client_id, data)
    await db.commit()
    return pmt


@router.get("/{client_id}/payments", response_model=dict)
async def payment_history(
    client_id: uuid.UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    items, total = await payment_repository.get_payment_history(
        db, client_id, current_user.id, offset=offset, limit=limit
    )
    return {
        "items": [PaymentResponse.model_validate(p) for p in items],
        "total": total, "offset": offset, "limit": limit,
    }


# ── Résumé heures ─────────────────────────────────────────────────────────────

@router.get("/{client_id}/hours", response_model=HoursSummary)
async def get_hours(
    client_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    return await payment_service.get_hours_summary(db, current_user, client_id)

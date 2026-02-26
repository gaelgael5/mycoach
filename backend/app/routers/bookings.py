"""Router réservations — B2-21."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user, require_coach, require_client
from app.database import get_db
from app.models.user import User
from app.repositories import booking_repository
from app.schemas.booking import (
    BookingCreate, BookingResponse, CancellationRequest,
)
from app.schemas.common import MessageResponse
from app.services import booking_service
from app.services.booking_service import (
    BookingNotFoundError, InvalidTransitionError,
    NotAuthorizedError, SlotFullError,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _booking_err(e: Exception) -> HTTPException:
    if isinstance(e, BookingNotFoundError):
        return HTTPException(status_code=404, detail=str(e))
    if isinstance(e, NotAuthorizedError):
        return HTTPException(status_code=403, detail=str(e))
    if isinstance(e, InvalidTransitionError):
        return HTTPException(status_code=422, detail=str(e))
    if isinstance(e, SlotFullError):
        return HTTPException(status_code=409, detail=str(e))
    return HTTPException(status_code=500, detail=str(e))


# ── Création (client) ──────────────────────────────────────────────────────────

@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(
    data: BookingCreate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await booking_service.create_booking(db, current_user, data)
        await db.commit()
        await db.refresh(booking)
        return booking
    except (BookingNotFoundError, InvalidTransitionError, SlotFullError) as e:
        raise _booking_err(e)


# ── Listing (client ou coach) ──────────────────────────────────────────────────

@router.get("")
async def list_bookings(
    status: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == "coach":
        items, total = await booking_repository.get_by_coach(
            db, current_user.id, status=status, offset=offset, limit=limit
        )
    else:
        items, total = await booking_repository.get_by_client(
            db, current_user.id, status=status, offset=offset, limit=limit
        )
    return {
        "items": [BookingResponse.model_validate(b) for b in items],
        "total": total, "offset": offset, "limit": limit,
    }


# ── Actions coach ──────────────────────────────────────────────────────────────

@router.post("/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await booking_service.confirm_booking(db, current_user, booking_id)
        await db.commit()
        await db.refresh(booking)
        return booking
    except Exception as e:
        raise _booking_err(e)


@router.post("/{booking_id}/reject", response_model=BookingResponse)
async def reject_booking(
    booking_id: uuid.UUID,
    data: CancellationRequest = CancellationRequest(),
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await booking_service.reject_booking(db, current_user, booking_id, data.reason)
        await db.commit()
        await db.refresh(booking)
        return booking
    except Exception as e:
        raise _booking_err(e)


@router.post("/{booking_id}/done", response_model=BookingResponse)
async def mark_done(
    booking_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await booking_service.mark_done(db, current_user, booking_id)
        await db.commit()
        await db.refresh(booking)
        return booking
    except Exception as e:
        raise _booking_err(e)


@router.post("/{booking_id}/no-show", response_model=BookingResponse)
async def mark_no_show(
    booking_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await booking_service.mark_no_show(db, current_user, booking_id)
        await db.commit()
        await db.refresh(booking)
        return booking
    except Exception as e:
        raise _booking_err(e)


@router.post("/{booking_id}/waive-penalty", response_model=BookingResponse)
async def waive_penalty(
    booking_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        booking = await booking_service.waive_penalty(db, current_user, booking_id)
        await db.commit()
        await db.refresh(booking)
        return booking
    except Exception as e:
        raise _booking_err(e)


# ── Annulation (coach ou client) ───────────────────────────────────────────────

@router.delete("/{booking_id}", response_model=BookingResponse)
async def cancel_booking(
    booking_id: uuid.UUID,
    data: CancellationRequest = CancellationRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        if current_user.role == "coach":
            booking = await booking_service.coach_cancel_booking(
                db, current_user, booking_id, data.reason
            )
        else:
            booking = await booking_service.client_cancel_booking(
                db, current_user, booking_id
            )
        await db.commit()
        await db.refresh(booking)
        return booking
    except Exception as e:
        raise _booking_err(e)

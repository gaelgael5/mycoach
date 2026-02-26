"""Router liste d'attente — B2-22."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user, require_client
from app.database import get_db
from app.models.user import User
from app.repositories import waitlist_repository
from app.schemas.booking import WaitlistJoinRequest, WaitlistEntryResponse
from app.schemas.common import MessageResponse
from app.services import waitlist_service
from app.services.waitlist_service import (
    AlreadyInWaitlistError, WaitlistEntryNotFoundError, ConfirmationWindowExpiredError
)

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


@router.post("", response_model=WaitlistEntryResponse, status_code=201)
async def join_waitlist(
    data: WaitlistJoinRequest,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    try:
        entry = await waitlist_service.join_waitlist(
            db, current_user, data.coach_id, data.slot_datetime
        )
        await db.commit()
        await db.refresh(entry)
        return entry
    except AlreadyInWaitlistError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=list[WaitlistEntryResponse])
async def my_waitlist(
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    return await waitlist_repository.get_by_client(db, current_user.id)


@router.post("/{entry_id}/confirm", response_model=WaitlistEntryResponse)
async def confirm_from_waitlist(
    entry_id: uuid.UUID,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    try:
        entry = await waitlist_service.confirm_from_waitlist(db, current_user, entry_id)
        await db.commit()
        await db.refresh(entry)
        return entry
    except WaitlistEntryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConfirmationWindowExpiredError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{entry_id}", response_model=MessageResponse)
async def leave_waitlist(
    entry_id: uuid.UUID,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    try:
        await waitlist_service.leave_waitlist(db, current_user, entry_id)
        await db.commit()
        return {"message": "Vous avez quitté la liste d'attente"}
    except WaitlistEntryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{coach_id}/{slot_datetime}", response_model=list[WaitlistEntryResponse])
async def get_slot_waitlist(
    coach_id: uuid.UUID,
    slot_datetime: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Vue coach : liste d'attente pour un créneau donné."""
    if current_user.role != "coach" or current_user.id != coach_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(slot_datetime)
    except ValueError:
        raise HTTPException(status_code=422, detail="Format datetime invalide (ISO 8601)")
    return await waitlist_repository.get_all_for_slot(db, coach_id, dt)

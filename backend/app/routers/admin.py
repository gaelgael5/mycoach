"""Router admin — B3-14 (validation machines)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.machine import Machine
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.performance import MachineResponse

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(current_user: User) -> User:
    """Seuls les admins peuvent valider des machines (rôle 'admin')."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs")
    return current_user


@router.get("/machines/pending", response_model=list[MachineResponse])
async def list_pending_machines(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    q = select(Machine).where(Machine.validated.is_(False)).order_by(Machine.id)
    machines = (await db.execute(q)).scalars().all()
    return machines


@router.post("/machines/{machine_id}/validate", response_model=MachineResponse)
async def validate_machine(
    machine_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    q = select(Machine).where(Machine.id == machine_id)
    machine = (await db.execute(q)).scalar_one_or_none()
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine introuvable")
    machine.validated = True
    machine.validated_by_id = current_user.id
    await db.commit()
    await db.refresh(machine)
    return machine


@router.post("/machines/{machine_id}/reject", response_model=MessageResponse)
async def reject_machine(
    machine_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    q = select(Machine).where(Machine.id == machine_id)
    machine = (await db.execute(q)).scalar_one_or_none()
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine introuvable")
    await db.delete(machine)
    await db.commit()
    return {"message": "Machine rejetée et supprimée"}

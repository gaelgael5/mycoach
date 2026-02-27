"""Router admin — B3-14 (validation machines) + blocklist domaines email."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.machine import Machine
from app.models.user import User
from app.repositories import blocked_domain_repository
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


# ---------------------------------------------------------------------------
# Blocklist domaines email — Schémas
# ---------------------------------------------------------------------------

class BlockedDomainCreate(BaseModel):
    domain: str
    reason: str | None = None


class BlockedDomainResponse(BaseModel):
    id: uuid.UUID
    domain: str
    reason: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Blocklist domaines email — Endpoints
# ---------------------------------------------------------------------------

@router.get("/blocked-domains", response_model=list[BlockedDomainResponse])
async def list_blocked_domains(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les domaines bloqués (admin seulement)."""
    _require_admin(current_user)
    return await blocked_domain_repository.list_all(db)


@router.post("/blocked-domains", response_model=BlockedDomainResponse, status_code=201)
async def add_blocked_domain(
    data: BlockedDomainCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ajoute un domaine à la blocklist (admin seulement)."""
    _require_admin(current_user)
    try:
        entry = await blocked_domain_repository.add(db, data.domain, data.reason)
        await db.commit()
        await db.refresh(entry)
        return entry
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ce domaine est déjà dans la liste")


@router.delete("/blocked-domains/{domain}", status_code=204)
async def remove_blocked_domain(
    domain: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Supprime un domaine de la blocklist (admin seulement)."""
    _require_admin(current_user)
    deleted = await blocked_domain_repository.remove(db, domain)
    await db.commit()
    if not deleted:
        raise HTTPException(status_code=404, detail="Domaine introuvable")

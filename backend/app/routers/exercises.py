"""Router exercices & machines — B3-13."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.repositories import performance_repository as repo
from app.schemas.performance import ExerciseTypeResponse, MachineResponse, MachineSubmit

router = APIRouter(tags=["exercises"])


# ── Exercices ──────────────────────────────────────────────────────────────────

@router.get("/exercises", response_model=dict)
async def search_exercises(
    q: str | None = Query(None, description="Recherche sur le name_key"),
    category: str | None = Query(None),
    difficulty: str | None = Query(None),
    muscle: str | None = Query(None, description="Groupe musculaire primaire"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    items, total = await repo.search_exercises(
        db, q=q, category=category, difficulty=difficulty,
        muscle=muscle, offset=offset, limit=limit,
    )
    return {
        "items": [ExerciseTypeResponse.model_validate(e) for e in items],
        "total": total, "offset": offset, "limit": limit,
    }


@router.get("/exercises/{exercise_id}", response_model=ExerciseTypeResponse)
async def get_exercise(
    exercise_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    ex = await repo.get_exercise_by_id(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercice introuvable")
    return ex


# ── Machines ───────────────────────────────────────────────────────────────────

@router.get("/machines/qr/{qr_hash}", response_model=MachineResponse)
async def get_machine_by_qr(qr_hash: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.machine import Machine
    q = select(Machine).where(Machine.qr_code_hash == qr_hash, Machine.validated.is_(True))
    machine = (await db.execute(q)).scalar_one_or_none()
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine introuvable")
    return machine


@router.post("/machines/submit", response_model=MachineResponse, status_code=201)
async def submit_machine(
    data: MachineSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.machine import Machine
    machine = Machine(
        id=uuid.uuid4(),
        type_key=data.type_key,
        brand=data.brand,
        model=data.model_name,
        qr_code_hash=data.qr_code_hash,
        validated=False,
        submitted_by_id=current_user.id,
    )
    db.add(machine)
    await db.commit()
    await db.refresh(machine)
    return machine

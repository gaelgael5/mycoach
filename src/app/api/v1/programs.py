"""Programs endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.models.tables import Program, ProgramSession, Exercise, ProgramAssignment, Client, Coach
from app.api.deps import get_current_coach
from app.schemas.program import (
    ProgramCreate, ProgramUpdate, ProgramRead, ProgramReadDetail,
    ProgramAssign, ProgramAssignmentRead,
    SessionCreate, SessionUpdate, SessionRead, SessionReadBrief,
    ExerciseCreate, ExerciseUpdate, ExerciseRead,
)

router = APIRouter(prefix="/programs", tags=["programs"])


@router.post("", response_model=ProgramRead, status_code=201)
async def create_program(
    body: ProgramCreate,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    program = Program(coach_id=coach.id, **body.model_dump())
    db.add(program)
    await db.flush()
    await db.refresh(program)
    return program


@router.get("", response_model=list[ProgramRead])
async def list_programs(
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Program).where(Program.coach_id == coach.id).order_by(Program.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{program_id}", response_model=ProgramReadDetail)
async def get_program(
    program_id: uuid.UUID,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Program)
        .where(Program.id == program_id, Program.coach_id == coach.id)
        .options(selectinload(Program.sessions).selectinload(ProgramSession.exercises))
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


@router.patch("/{program_id}", response_model=ProgramRead)
async def update_program(
    program_id: uuid.UUID,
    body: ProgramUpdate,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Program).where(Program.id == program_id, Program.coach_id == coach.id)
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(program, k, v)
    await db.flush()
    await db.refresh(program)
    return program


@router.delete("/{program_id}", status_code=204)
async def delete_program(
    program_id: uuid.UUID,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Program).where(Program.id == program_id, Program.coach_id == coach.id)
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    await db.delete(program)


@router.post("/{program_id}/duplicate", response_model=ProgramRead, status_code=201)
async def duplicate_program(
    program_id: uuid.UUID,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Program)
        .where(Program.id == program_id, Program.coach_id == coach.id)
        .options(selectinload(Program.sessions).selectinload(ProgramSession.exercises))
    )
    original = result.scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Program not found")

    new_program = Program(
        coach_id=coach.id,
        name=f"{original.name} (copy)",
        description=original.description,
        duration_weeks=original.duration_weeks,
        is_template=original.is_template,
    )
    db.add(new_program)
    await db.flush()

    for sess in original.sessions:
        new_sess = ProgramSession(
            program_id=new_program.id,
            day_number=sess.day_number,
            name=sess.name,
            notes=sess.notes,
        )
        db.add(new_sess)
        await db.flush()
        for ex in sess.exercises:
            new_ex = Exercise(
                session_id=new_sess.id,
                name=ex.name,
                sets=ex.sets,
                reps=ex.reps,
                weight=ex.weight,
                rest_seconds=ex.rest_seconds,
                notes=ex.notes,
                order=ex.order,
            )
            db.add(new_ex)

    await db.flush()
    await db.refresh(new_program)
    return new_program


@router.post("/{program_id}/assign", response_model=list[ProgramAssignmentRead], status_code=201)
async def assign_program(
    program_id: uuid.UUID,
    body: ProgramAssign,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Program).where(Program.id == program_id, Program.coach_id == coach.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Program not found")

    assignments = []
    for cid in body.client_ids:
        # Verify client belongs to coach
        cr = await db.execute(select(Client).where(Client.id == cid, Client.coach_id == coach.id))
        if not cr.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"Client {cid} not found")
        # Check not already assigned
        existing = await db.execute(
            select(ProgramAssignment).where(
                ProgramAssignment.program_id == program_id,
                ProgramAssignment.client_id == cid,
            )
        )
        if existing.scalar_one_or_none():
            continue
        a = ProgramAssignment(program_id=program_id, client_id=cid)
        db.add(a)
        await db.flush()
        await db.refresh(a)
        assignments.append(a)
    return assignments


# --- Sessions ---
@router.post("/{program_id}/sessions", response_model=SessionReadBrief, status_code=201)
async def create_session(
    program_id: uuid.UUID,
    body: SessionCreate,
    coach: Coach = Depends(get_current_coach),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Program).where(Program.id == program_id, Program.coach_id == coach.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Program not found")
    sess = ProgramSession(program_id=program_id, **body.model_dump())
    db.add(sess)
    await db.flush()
    await db.refresh(sess)
    return sess

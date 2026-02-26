"""Router programmes d'entraînement — B4-11."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user, require_coach, require_client
from app.database import get_db
from app.models.user import User
from app.schemas.program import (
    AssignPlanRequest, ClientProgressResponse,
    GenerateProgramRequest, PlanAssignmentResponse,
    WorkoutPlanCreate, WorkoutPlanResponse, WorkoutPlanSummary,
)
from app.schemas.common import MessageResponse
from app.services import program_service
from app.services.program_service import (
    PlanNotFoundError, NotAuthorizedError, PlanAlreadyArchivedError
)

router = APIRouter(tags=["programs"])


def _plan_err(e: Exception) -> HTTPException:
    if isinstance(e, PlanNotFoundError):
        return HTTPException(status_code=404, detail=str(e))
    if isinstance(e, NotAuthorizedError):
        return HTTPException(status_code=403, detail=str(e))
    if isinstance(e, PlanAlreadyArchivedError):
        return HTTPException(status_code=422, detail=str(e))
    return HTTPException(status_code=500, detail=str(e))


# ── Client : programme courant ─────────────────────────────────────────────────

@router.get("/clients/program", response_model=PlanAssignmentResponse | None)
async def get_my_program(
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    return await program_service.get_my_program(db, current_user)


@router.post("/clients/program/generate", response_model=PlanAssignmentResponse, status_code=201)
async def generate_my_program(
    data: GenerateProgramRequest,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    """Génère (ou régénère) un programme IA pour le client."""
    from app.services.program_generator_service import generate_weekly_program
    from app.repositories import program_repository as repo
    from datetime import date

    plan = await generate_weekly_program(
        db,
        goal=data.goal,
        frequency_per_week=data.frequency_per_week,
        level=data.level,
        client_id=current_user.id,
    )
    assignment = await repo.assign_plan(
        db,
        plan_id=plan.id,
        client_id=current_user.id,
        start_date=date.today(),
        mode="replace_ai",
        assigned_by_id=None,
    )
    await db.commit()
    return await repo.get_current_assignment(db, current_user.id)


@router.post("/clients/program/recalibrate", response_model=PlanAssignmentResponse)
async def recalibrate_program(
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    result = await program_service.recalibrate_my_program(db, current_user)
    await db.commit()
    return result


# ── Coach : CRUD plans ─────────────────────────────────────────────────────────

@router.get("/coaches/programs", response_model=list[WorkoutPlanSummary])
async def list_my_plans(
    include_archived: bool = Query(False),
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    plans = await program_service.list_plans(db, current_user, include_archived=include_archived)
    return [
        WorkoutPlanSummary(
            **{k: getattr(p, k) for k in WorkoutPlanSummary.model_fields
               if k != "sessions_count" and hasattr(p, k)},
            sessions_count=len(p.planned_sessions),
        )
        for p in plans
    ]


@router.post("/coaches/programs", response_model=WorkoutPlanResponse, status_code=201)
async def create_plan(
    data: WorkoutPlanCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    plan = await program_service.create_plan(db, current_user, data)
    await db.commit()
    return plan


@router.get("/coaches/programs/{plan_id}", response_model=WorkoutPlanResponse)
async def get_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await program_service.get_plan(db, current_user, plan_id)
    except Exception as e:
        raise _plan_err(e)


@router.post("/coaches/programs/{plan_id}/archive", response_model=MessageResponse)
async def archive_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        await program_service.archive_plan(db, current_user, plan_id)
        await db.commit()
        return {"message": "Plan archivé"}
    except Exception as e:
        raise _plan_err(e)


@router.post("/coaches/programs/{plan_id}/duplicate", response_model=WorkoutPlanResponse)
async def duplicate_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        plan = await program_service.duplicate_plan(db, current_user, plan_id)
        await db.commit()
        return plan
    except Exception as e:
        raise _plan_err(e)


@router.post("/coaches/programs/{plan_id}/assign", response_model=PlanAssignmentResponse)
async def assign_plan(
    plan_id: uuid.UUID,
    data: AssignPlanRequest,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        assignment = await program_service.assign_to_client(
            db, current_user, plan_id, data.client_id, data.start_date, data.mode
        )
        await db.commit()
        # Re-fetch avec joinedload pour éviter MissingGreenlet lors de la sérialisation
        from app.repositories import program_repository as repo2
        return await repo2.get_assignment_by_id(db, assignment.id)
    except Exception as e:
        raise _plan_err(e)


@router.get(
    "/coaches/clients/{client_id}/program-progress",
    response_model=ClientProgressResponse,
)
async def get_client_progress(
    client_id: uuid.UUID,
    plan_id: uuid.UUID = Query(...),
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    progress = await program_service.get_client_progress(db, current_user, client_id, plan_id)
    return ClientProgressResponse(plan_id=plan_id, **progress)

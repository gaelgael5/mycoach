"""Coach profile router."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.tables import Coach
from app.api.deps import get_current_coach
from app.schemas.coach import CoachRead, CoachUpdate

router = APIRouter(prefix="/coach", tags=["coach"])


@router.get("/me", response_model=CoachRead)
async def get_me(coach: Coach = Depends(get_current_coach)):
    """Get the authenticated coach's profile."""
    return coach


@router.patch("/me", response_model=CoachRead)
async def update_me(
    body: CoachUpdate,
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Update the authenticated coach's profile."""
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(coach, field, value)
    await db.flush()
    await db.refresh(coach)
    return coach

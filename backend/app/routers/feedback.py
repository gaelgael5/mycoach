"""Router — Feedback utilisateur (suggestions & rapports de bugs)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services import feedback_service

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soumettre un feedback (suggestion ou rapport de bug)."""
    feedback = await feedback_service.submit_feedback(db, current_user.id, data)
    await db.commit()
    await db.refresh(feedback)
    return feedback


@router.get("/mine", response_model=list[FeedbackResponse])
async def my_feedbacks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste mes feedbacks soumis."""
    return await feedback_service.get_my_feedbacks(db, current_user.id)

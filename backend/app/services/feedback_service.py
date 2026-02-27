"""Service — Feedback utilisateur."""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_feedback import UserFeedback
from app.repositories import feedback_repository
from app.schemas.feedback import FeedbackAdminUpdate, FeedbackCreate


class FeedbackNotFoundError(Exception):
    """Le feedback demandé n'existe pas."""


async def submit_feedback(
    db: AsyncSession,
    user_id: Optional[uuid.UUID],
    data: FeedbackCreate,
) -> UserFeedback:
    return await feedback_repository.create(db, user_id, data)


async def list_feedback(
    db: AsyncSession,
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[UserFeedback]:
    return await feedback_repository.list_all(db, type_filter, status_filter, limit, offset)


async def get_my_feedbacks(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[UserFeedback]:
    return await feedback_repository.list_by_user(db, user_id)


async def update_feedback(
    db: AsyncSession,
    feedback_id: uuid.UUID,
    data: FeedbackAdminUpdate,
) -> UserFeedback:
    feedback = await feedback_repository.get_by_id(db, feedback_id)
    if feedback is None:
        raise FeedbackNotFoundError(f"Feedback {feedback_id} introuvable")
    return await feedback_repository.update_status(db, feedback, data)

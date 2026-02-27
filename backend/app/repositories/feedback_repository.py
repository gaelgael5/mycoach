"""Repository — UserFeedback."""
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_feedback import UserFeedback
from app.schemas.feedback import FeedbackAdminUpdate, FeedbackCreate


async def create(
    db: AsyncSession,
    user_id: Optional[uuid.UUID],
    data: FeedbackCreate,
) -> UserFeedback:
    feedback = UserFeedback(
        user_id=user_id,
        type=data.type,
        title=data.title,
        description=data.description,
        app_version=data.app_version,
        platform=data.platform,
    )
    db.add(feedback)
    await db.flush()
    await db.refresh(feedback)
    return feedback


async def get_by_id(
    db: AsyncSession,
    feedback_id: uuid.UUID,
) -> UserFeedback | None:
    q = select(UserFeedback).where(UserFeedback.id == feedback_id)
    return (await db.execute(q)).scalar_one_or_none()


async def list_all(
    db: AsyncSession,
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[UserFeedback]:
    q = select(UserFeedback).order_by(UserFeedback.created_at.desc())
    if type_filter:
        q = q.where(UserFeedback.type == type_filter)
    if status_filter:
        q = q.where(UserFeedback.status == status_filter)
    q = q.limit(limit).offset(offset)
    return list((await db.execute(q)).scalars().all())


async def list_by_user(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[UserFeedback]:
    q = (
        select(UserFeedback)
        .where(UserFeedback.user_id == user_id)
        .order_by(UserFeedback.created_at.desc())
    )
    return list((await db.execute(q)).scalars().all())


async def update_status(
    db: AsyncSession,
    feedback: UserFeedback,
    data: FeedbackAdminUpdate,
) -> UserFeedback:
    if data.status is not None:
        feedback.status = data.status
    if data.admin_note is not None:
        feedback.admin_note = data.admin_note
    await db.flush()
    await db.refresh(feedback)
    return feedback

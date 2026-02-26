"""Repository client — B2-10."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_profile import ClientProfile
from app.models.client_questionnaire import ClientQuestionnaire


async def get_profile_by_user_id(
    db: AsyncSession, user_id: uuid.UUID
) -> ClientProfile | None:
    q = select(ClientProfile).where(ClientProfile.user_id == user_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def create_profile(
    db: AsyncSession, user_id: uuid.UUID, **kwargs: Any
) -> ClientProfile:
    profile = ClientProfile(id=uuid.uuid4(), user_id=user_id, **kwargs)
    db.add(profile)
    await db.flush()
    return profile


async def update_profile(
    db: AsyncSession, profile: ClientProfile, **kwargs: Any
) -> ClientProfile:
    for k, v in kwargs.items():
        setattr(profile, k, v)
    await db.flush()
    return profile


# ── Questionnaire ──────────────────────────────────────────────────────────────

async def get_questionnaire(
    db: AsyncSession, user_id: uuid.UUID
) -> ClientQuestionnaire | None:
    q = select(ClientQuestionnaire).where(ClientQuestionnaire.client_id == user_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def upsert_questionnaire(
    db: AsyncSession, user_id: uuid.UUID, **kwargs: Any
) -> ClientQuestionnaire:
    questionnaire = await get_questionnaire(db, user_id)
    if questionnaire is None:
        questionnaire = ClientQuestionnaire(
            id=uuid.uuid4(), client_id=user_id, **kwargs
        )
        db.add(questionnaire)
    else:
        for k, v in kwargs.items():
            setattr(questionnaire, k, v)
    await db.flush()
    return questionnaire

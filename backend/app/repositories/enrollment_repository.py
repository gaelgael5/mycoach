"""Repository — liens d'enrôlement coach (Phase 9)."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coach_enrollment_token import CoachEnrollmentToken
from app.schemas.enrollment import EnrollmentTokenCreate


async def create_token(
    db: AsyncSession,
    coach_id: uuid.UUID,
    data: EnrollmentTokenCreate,
) -> CoachEnrollmentToken:
    """Crée un token d'enrôlement pour un coach."""
    token = CoachEnrollmentToken(
        coach_id=coach_id,
        label=data.label,
        expires_at=data.expires_at,
        max_uses=data.max_uses,
    )
    db.add(token)
    await db.flush()
    return token


async def get_by_token(
    db: AsyncSession,
    token: str,
) -> CoachEnrollmentToken | None:
    """Récupère un token par sa valeur."""
    result = await db.execute(
        select(CoachEnrollmentToken).where(CoachEnrollmentToken.token == token)
    )
    return result.scalar_one_or_none()


async def get_by_id(
    db: AsyncSession,
    token_id: uuid.UUID,
    coach_id: uuid.UUID,
) -> CoachEnrollmentToken | None:
    """Récupère un token par son ID, vérifiant l'ownership du coach."""
    result = await db.execute(
        select(CoachEnrollmentToken).where(
            CoachEnrollmentToken.id == token_id,
            CoachEnrollmentToken.coach_id == coach_id,
        )
    )
    return result.scalar_one_or_none()


async def list_by_coach(
    db: AsyncSession,
    coach_id: uuid.UUID,
) -> list[CoachEnrollmentToken]:
    """Liste tous les tokens d'un coach."""
    result = await db.execute(
        select(CoachEnrollmentToken)
        .where(CoachEnrollmentToken.coach_id == coach_id)
        .order_by(CoachEnrollmentToken.created_at.desc())
    )
    return list(result.scalars().all())


async def increment_uses(
    db: AsyncSession,
    token: CoachEnrollmentToken,
) -> None:
    """Incrémente le compteur d'utilisations."""
    token.uses_count += 1
    await db.flush()


async def deactivate(
    db: AsyncSession,
    token: CoachEnrollmentToken,
) -> None:
    """Désactive un token (active = False)."""
    token.active = False
    await db.flush()

"""Repository intégrations OAuth + mesures corporelles — Phase 5."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration import BodyMeasurement, OAuthToken


# ── OAuth Tokens ───────────────────────────────────────────────────────────────

async def upsert_token(
    db: AsyncSession,
    user_id: uuid.UUID,
    provider: str,
    access_token_enc: str,
    refresh_token_enc: str | None,
    expires_at: datetime | None,
    scope: str | None,
) -> OAuthToken:
    """Crée ou remplace le token OAuth d'un user × provider (upsert)."""
    q = select(OAuthToken).where(
        OAuthToken.user_id == user_id,
        OAuthToken.provider == provider,
    )
    existing = (await db.execute(q)).scalar_one_or_none()
    if existing:
        existing.access_token_enc = access_token_enc
        existing.refresh_token_enc = refresh_token_enc
        existing.expires_at = expires_at
        existing.scope = scope
        await db.flush()
        return existing
    token = OAuthToken(
        id=uuid.uuid4(),
        user_id=user_id,
        provider=provider,
        access_token_enc=access_token_enc,
        refresh_token_enc=refresh_token_enc,
        expires_at=expires_at,
        scope=scope,
    )
    db.add(token)
    await db.flush()
    return token


async def get_token(
    db: AsyncSession, user_id: uuid.UUID, provider: str
) -> OAuthToken | None:
    q = select(OAuthToken).where(
        OAuthToken.user_id == user_id,
        OAuthToken.provider == provider,
    )
    return (await db.execute(q)).scalar_one_or_none()


async def delete_token(
    db: AsyncSession, user_id: uuid.UUID, provider: str
) -> bool:
    q = delete(OAuthToken).where(
        OAuthToken.user_id == user_id,
        OAuthToken.provider == provider,
    )
    result = await db.execute(q)
    await db.flush()
    return result.rowcount > 0


async def list_user_tokens(
    db: AsyncSession, user_id: uuid.UUID
) -> list[OAuthToken]:
    q = select(OAuthToken).where(OAuthToken.user_id == user_id)
    return list((await db.execute(q)).scalars().all())


# ── Body Measurements ──────────────────────────────────────────────────────────

async def add_measurement(db: AsyncSession, **kwargs) -> BodyMeasurement:
    m = BodyMeasurement(id=uuid.uuid4(), **kwargs)
    db.add(m)
    await db.flush()
    return m


async def list_measurements(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    limit: int = 30,
    offset: int = 0,
) -> list[BodyMeasurement]:
    q = (
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.measured_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list((await db.execute(q)).scalars().all())

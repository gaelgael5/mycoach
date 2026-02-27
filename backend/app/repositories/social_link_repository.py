"""Repository — Liens réseaux sociaux (Phase 7)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_link import SocialLink


async def get_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[SocialLink]:
    """Retourne tous les liens d'un utilisateur."""
    result = await db.execute(
        select(SocialLink).where(SocialLink.user_id == user_id).order_by(SocialLink.platform)
    )
    return list(result.scalars().all())


async def get_by_user_platform(
    db: AsyncSession, user_id: uuid.UUID, platform: str
) -> SocialLink | None:
    """Retourne le lien d'un utilisateur pour une plateforme donnée."""
    result = await db.execute(
        select(SocialLink).where(
            SocialLink.user_id == user_id,
            SocialLink.platform == platform,
        )
    )
    return result.scalar_one_or_none()


async def upsert(
    db: AsyncSession, user_id: uuid.UUID, platform: str, url: str
) -> SocialLink:
    """Insert ou update le lien (UPSERT sur user_id + platform)."""
    now = datetime.now(timezone.utc)
    stmt = (
        insert(SocialLink)
        .values(
            id=uuid.uuid4(),
            user_id=user_id,
            platform=platform,
            url=url,
            created_at=now,
            updated_at=now,
        )
        .on_conflict_do_update(
            constraint="uq_user_social_links_user_platform",
            set_={"url": url, "updated_at": now},
        )
        .returning(SocialLink)
    )
    result = await db.execute(stmt)
    await db.flush()
    row = result.scalar_one()
    return row


async def delete_link(
    db: AsyncSession, user_id: uuid.UUID, platform: str
) -> bool:
    """Supprime le lien. Retourne True si supprimé, False si introuvable."""
    result = await db.execute(
        delete(SocialLink)
        .where(
            SocialLink.user_id == user_id,
            SocialLink.platform == platform,
        )
        .returning(SocialLink.id)
    )
    await db.flush()
    return result.scalar_one_or_none() is not None

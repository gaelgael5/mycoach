"""Repository — Liens réseaux sociaux (Phase 7)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_link import SocialLink
from app.schemas.social_link import SocialLinkUpdate


async def get_by_user(db: AsyncSession, user_id: uuid.UUID) -> list[SocialLink]:
    """Retourne tous les liens d'un utilisateur, triés par position puis created_at."""
    result = await db.execute(
        select(SocialLink)
        .where(SocialLink.user_id == user_id)
        .order_by(SocialLink.position, SocialLink.created_at)
    )
    return list(result.scalars().all())


async def get_by_user_public(db: AsyncSession, user_id: uuid.UUID) -> list[SocialLink]:
    """Retourne uniquement les liens publics d'un utilisateur."""
    result = await db.execute(
        select(SocialLink)
        .where(SocialLink.user_id == user_id, SocialLink.visibility == "public")
        .order_by(SocialLink.position, SocialLink.created_at)
    )
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, link_id: uuid.UUID, user_id: uuid.UUID
) -> SocialLink | None:
    """Retourne un lien par son ID (vérification ownership user_id)."""
    result = await db.execute(
        select(SocialLink).where(
            SocialLink.id == link_id,
            SocialLink.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def count_by_user(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Compte le nombre total de liens pour un utilisateur."""
    result = await db.execute(
        select(func.count()).where(SocialLink.user_id == user_id)
    )
    return result.scalar_one()


async def upsert_standard(
    db: AsyncSession,
    user_id: uuid.UUID,
    platform: str,
    label: Optional[str],
    url: str,
    visibility: str,
    position: int,
) -> SocialLink:
    """UPSERT sur (user_id, platform) via index partiel WHERE platform IS NOT NULL.

    Si la plateforme existe déjà → update url/label/visibility/position/updated_at.
    Sinon → insert.
    """
    now = datetime.now(timezone.utc)
    stmt = (
        insert(SocialLink)
        .values(
            id=uuid.uuid4(),
            user_id=user_id,
            platform=platform,
            label=label,
            url=url,
            visibility=visibility,
            position=position,
            created_at=now,
            updated_at=now,
        )
        .on_conflict_do_update(
            index_elements=["user_id", "platform"],
            index_where=SocialLink.platform.isnot(None),
            set_={
                "label": label,
                "url": url,
                "visibility": visibility,
                "position": position,
                "updated_at": now,
            },
        )
        .returning(SocialLink)
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.scalar_one()


async def create_custom(
    db: AsyncSession,
    user_id: uuid.UUID,
    label: str,
    url: str,
    visibility: str,
    position: int,
) -> SocialLink:
    """Crée un lien custom (platform=NULL). Plusieurs autorisés par user."""
    link = SocialLink(
        user_id=user_id,
        platform=None,
        label=label,
        url=url,
        visibility=visibility,
        position=position,
    )
    db.add(link)
    await db.flush()
    await db.refresh(link)
    return link


async def update_link(
    db: AsyncSession, link: SocialLink, data: SocialLinkUpdate
) -> SocialLink:
    """Met à jour les champs fournis d'un lien existant."""
    if data.url is not None:
        link.url = data.url
    if data.label is not None:
        link.label = data.label
    if data.visibility is not None:
        link.visibility = data.visibility
    if data.position is not None:
        link.position = data.position
    await db.flush()
    await db.refresh(link)
    return link


async def delete_link(
    db: AsyncSession, link_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    """Supprime un lien par son ID. Retourne True si supprimé, False si introuvable."""
    result = await db.execute(
        delete(SocialLink)
        .where(SocialLink.id == link_id, SocialLink.user_id == user_id)
        .returning(SocialLink.id)
    )
    await db.flush()
    return result.scalar_one_or_none() is not None

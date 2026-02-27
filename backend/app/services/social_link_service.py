"""Service — Liens réseaux sociaux (Phase 7)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_link import SocialLink
from app.repositories import social_link_repository


class LinkNotFoundError(Exception):
    """Le lien demandé n'existe pas."""


async def list_links(db: AsyncSession, user_id: uuid.UUID) -> list[SocialLink]:
    """Retourne tous les liens d'un utilisateur."""
    return await social_link_repository.get_by_user(db, user_id)


async def upsert_link(
    db: AsyncSession, user_id: uuid.UUID, platform: str, url: str
) -> SocialLink:
    """Ajoute ou remplace le lien pour la plateforme donnée."""
    return await social_link_repository.upsert(db, user_id, platform, url)


async def delete_link(
    db: AsyncSession, user_id: uuid.UUID, platform: str
) -> None:
    """Supprime le lien. Lève LinkNotFoundError si absent."""
    deleted = await social_link_repository.delete_link(db, user_id, platform)
    if not deleted:
        raise LinkNotFoundError(f"Lien '{platform}' introuvable pour cet utilisateur")

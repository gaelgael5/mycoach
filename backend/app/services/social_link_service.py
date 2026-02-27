"""Service — Liens réseaux sociaux (Phase 7)."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_link import SocialLink
from app.repositories import social_link_repository
from app.schemas.social_link import MAX_LINKS_PER_USER, SocialLinkCreate, SocialLinkUpdate


class LinkNotFoundError(Exception):
    """Le lien demandé n'existe pas."""


class TooManyLinksError(Exception):
    """L'utilisateur a atteint le maximum de liens autorisés."""


async def list_links(db: AsyncSession, user_id: uuid.UUID) -> list[SocialLink]:
    """Retourne tous les liens d'un utilisateur."""
    return await social_link_repository.get_by_user(db, user_id)


async def list_public_links(db: AsyncSession, user_id: uuid.UUID) -> list[SocialLink]:
    """Retourne uniquement les liens publics (pour affichage profil coach)."""
    return await social_link_repository.get_by_user_public(db, user_id)


async def create_or_upsert_link(
    db: AsyncSession, user_id: uuid.UUID, data: SocialLinkCreate
) -> SocialLink:
    """Crée ou met à jour un lien.

    - Plateforme standard → UPSERT (pas de comptage si existant)
    - Lien custom (platform=None) → INSERT toujours + vérif max 20
    """
    if data.platform is not None:
        # Standard : upsert sans vérifier le max (remplacement, pas ajout)
        return await social_link_repository.upsert_standard(
            db,
            user_id=user_id,
            platform=data.platform,
            label=data.label,
            url=data.url,
            visibility=data.visibility,
            position=data.position,
        )
    else:
        # Custom : vérifier max 20 avant d'insérer
        count = await social_link_repository.count_by_user(db, user_id)
        if count >= MAX_LINKS_PER_USER:
            raise TooManyLinksError(
                f"Maximum de {MAX_LINKS_PER_USER} liens atteint pour cet utilisateur"
            )
        return await social_link_repository.create_custom(
            db,
            user_id=user_id,
            label=data.label,  # type: ignore[arg-type]  # validé par pydantic
            url=data.url,
            visibility=data.visibility,
            position=data.position,
        )


async def update_link(
    db: AsyncSession, user_id: uuid.UUID, link_id: uuid.UUID, data: SocialLinkUpdate
) -> SocialLink:
    """Met à jour un lien existant. Lève LinkNotFoundError si absent ou n'appartient pas à l'user."""
    link = await social_link_repository.get_by_id(db, link_id, user_id)
    if link is None:
        raise LinkNotFoundError(f"Lien {link_id} introuvable")
    return await social_link_repository.update_link(db, link, data)


async def delete_link(
    db: AsyncSession, user_id: uuid.UUID, link_id: uuid.UUID
) -> None:
    """Supprime un lien par ID. Lève LinkNotFoundError si absent."""
    deleted = await social_link_repository.delete_link(db, link_id, user_id)
    if not deleted:
        raise LinkNotFoundError(f"Lien {link_id} introuvable")

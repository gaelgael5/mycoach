"""Router — Liens réseaux sociaux (Phase 7)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.social_link import SocialLinkCreate, SocialLinkResponse
from app.services import social_link_service
from app.services.social_link_service import LinkNotFoundError

router = APIRouter(prefix="/users/me/social-links", tags=["social-links"])


@router.get("/", response_model=list[SocialLinkResponse])
async def list_my_social_links(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste les liens réseaux sociaux de l'utilisateur connecté."""
    links = await social_link_service.list_links(db, current_user.id)
    return links


@router.post("/", response_model=SocialLinkResponse)
async def upsert_social_link(
    data: SocialLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ajoute ou remplace un lien réseau social."""
    link = await social_link_service.upsert_link(db, current_user.id, data.platform, data.url)
    await db.commit()
    # Re-fetch pour avoir l'objet frais après commit
    from app.repositories import social_link_repository
    link = await social_link_repository.get_by_user_platform(db, current_user.id, data.platform)
    return link


@router.delete("/{platform}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_link(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Supprime un lien réseau social."""
    try:
        await social_link_service.delete_link(db, current_user.id, platform)
        await db.commit()
    except LinkNotFoundError:
        raise HTTPException(status_code=404, detail="Lien introuvable")

"""Router — Liens réseaux sociaux (Phase 7).

Endpoints :
  GET    /users/me/social-links           → liste tous mes liens
  POST   /users/me/social-links           → créer ou mettre à jour un lien
  PUT    /users/me/social-links/{link_id} → modifier un lien existant par ID
  DELETE /users/me/social-links/{link_id} → supprimer un lien par ID
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.social_link import SocialLinkCreate, SocialLinkResponse, SocialLinkUpdate
from app.services import social_link_service
from app.services.social_link_service import LinkNotFoundError, TooManyLinksError

router = APIRouter(prefix="/users/me/social-links", tags=["social-links"])


@router.get("/", response_model=list[SocialLinkResponse])
async def list_my_social_links(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Liste tous les liens réseaux sociaux de l'utilisateur connecté."""
    return await social_link_service.list_links(db, current_user.id)


@router.post("/", response_model=SocialLinkResponse, status_code=status.HTTP_200_OK)
async def create_or_update_social_link(
    data: SocialLinkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ajoute ou remplace un lien réseau social.

    - Plateforme standard (platform=instagram…) → UPSERT, 1 seul par plateforme
    - Lien custom (platform=null, label requis) → INSERT, max 20 total
    """
    try:
        link = await social_link_service.create_or_upsert_link(db, current_user.id, data)
        await db.commit()
        await db.refresh(link)
        return link
    except TooManyLinksError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/{link_id}", response_model=SocialLinkResponse)
async def update_social_link(
    link_id: uuid.UUID,
    data: SocialLinkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Modifie un lien existant par son ID."""
    try:
        link = await social_link_service.update_link(db, current_user.id, link_id, data)
        await db.commit()
        await db.refresh(link)
        return link
    except LinkNotFoundError:
        raise HTTPException(status_code=404, detail="Lien introuvable")


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_link(
    link_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Supprime un lien réseau social par son ID."""
    try:
        await social_link_service.delete_link(db, current_user.id, link_id)
        await db.commit()
    except LinkNotFoundError:
        raise HTTPException(status_code=404, detail="Lien introuvable")

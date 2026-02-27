"""Router — Liens d'enrôlement coach (Phase 9)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_coach
from app.database import get_db
from app.schemas.enrollment import EnrollmentTokenCreate, EnrollmentTokenPublicInfo, EnrollmentTokenResponse
from app.services import enrollment_service
from app.services.enrollment_service import (
    EnrollmentTokenExhaustedError,
    EnrollmentTokenExpiredError,
    EnrollmentTokenInactiveError,
    EnrollmentTokenNotFoundError,
    build_enrollment_link,
)

router = APIRouter(tags=["enrollment"])


# ---------------------------------------------------------------------------
# Coach : gérer ses tokens
# ---------------------------------------------------------------------------

@router.post(
    "/coaches/me/enrollment-tokens",
    response_model=EnrollmentTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_enrollment_token(
    data: EnrollmentTokenCreate,
    current_user=Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    """Crée un nouveau lien d'enrôlement pour le coach authentifié."""
    token = await enrollment_service.create_token(db, current_user.id, data)
    await db.commit()
    await db.refresh(token)
    return {**token.__dict__, "enrollment_link": build_enrollment_link(token.token)}


@router.get(
    "/coaches/me/enrollment-tokens",
    response_model=list[EnrollmentTokenResponse],
)
async def list_enrollment_tokens(
    current_user=Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    """Liste les tokens d'enrôlement du coach authentifié."""
    tokens = await enrollment_service.list_tokens(db, current_user.id)
    return [{**t.__dict__, "enrollment_link": build_enrollment_link(t.token)} for t in tokens]


@router.delete(
    "/coaches/me/enrollment-tokens/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_enrollment_token(
    token_id: uuid.UUID,
    current_user=Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    """Désactive un lien d'enrôlement (ne le supprime pas)."""
    try:
        await enrollment_service.deactivate_token(db, current_user.id, token_id)
        await db.commit()
    except EnrollmentTokenNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token introuvable")


# ---------------------------------------------------------------------------
# Public : infos coach via token (pour l'écran de pré-inscription)
# ---------------------------------------------------------------------------

@router.get(
    "/enroll/{token}",
    response_model=EnrollmentTokenPublicInfo,
)
async def get_enrollment_info(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Retourne les infos publiques du coach pour l'écran de pré-inscription."""
    try:
        info = await enrollment_service.get_coach_info_for_token(db, token)
        return info
    except (
        EnrollmentTokenNotFoundError,
        EnrollmentTokenInactiveError,
        EnrollmentTokenExpiredError,
        EnrollmentTokenExhaustedError,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

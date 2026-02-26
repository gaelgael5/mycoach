"""Router clients — B2-20."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_client
from app.database import get_db
from app.models.user import User
from app.repositories import client_repository
from app.schemas.client import (
    ClientProfileCreate, ClientProfileUpdate, ClientProfileResponse,
    QuestionnaireCreate, QuestionnaireUpdate, QuestionnaireResponse,
    CoachingRequestCreate, CoachingRequestResponse,
)
from app.schemas.common import MessageResponse
from app.services import client_service
from app.services.client_service import (
    ProfileAlreadyExistsError, ProfileNotFoundError
)

router = APIRouter(prefix="/clients", tags=["clients"])


# ── Profil ─────────────────────────────────────────────────────────────────────

@router.post("/profile", response_model=ClientProfileResponse, status_code=201)
async def create_profile(
    data: ClientProfileCreate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await client_service.create_profile(db, current_user, data)
        await db.commit()
        await db.refresh(profile)
        return profile
    except ProfileAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/profile", response_model=ClientProfileResponse)
async def get_profile(
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await client_service.get_my_profile(db, current_user)
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profil client introuvable")


@router.put("/profile", response_model=ClientProfileResponse)
async def update_profile(
    data: ClientProfileUpdate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await client_service.update_profile(db, current_user, data)
        await db.commit()
        await db.refresh(profile)
        return profile
    except ProfileNotFoundError:
        raise HTTPException(status_code=404, detail="Profil client introuvable")


# ── Questionnaire ──────────────────────────────────────────────────────────────

@router.post("/questionnaire", response_model=QuestionnaireResponse, status_code=201)
async def create_questionnaire(
    data: QuestionnaireCreate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    q = await client_service.upsert_questionnaire(db, current_user, data)
    await db.commit()
    await db.refresh(q)
    return q


@router.put("/questionnaire", response_model=QuestionnaireResponse)
async def update_questionnaire(
    data: QuestionnaireUpdate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    q = await client_service.upsert_questionnaire(db, current_user, data)
    await db.commit()
    await db.refresh(q)
    return q


@router.get("/questionnaire", response_model=QuestionnaireResponse)
async def get_questionnaire(
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    q = await client_repository.get_questionnaire(db, current_user.id)
    if q is None:
        raise HTTPException(status_code=404, detail="Questionnaire introuvable")
    return q


# ── Recherche coaches ──────────────────────────────────────────────────────────

@router.get("/coaches/search")
async def search_coaches(
    country: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    return await client_service.search_coaches(
        db, country=country, offset=offset, limit=limit
    )


# ── Demandes de coaching ──────────────────────────────────────────────────────

@router.post("/coaching-requests", response_model=CoachingRequestResponse, status_code=201)
async def send_coaching_request(
    data: CoachingRequestCreate,
    current_user: User = Depends(require_client),
    db: AsyncSession = Depends(get_db),
):
    from app.services.client_service import CoachNotFoundError
    try:
        req = await client_service.send_discovery_request(
            db, current_user, data.coach_id, data.client_message, data.discovery_slot
        )
        await db.commit()
        await db.refresh(req)
        return req
    except CoachNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

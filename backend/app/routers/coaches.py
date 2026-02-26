"""Router coaches — B1-25."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_coach
from app.database import get_db
from app.models.user import User
from app.schemas.coach import (
    CoachProfileCreate, CoachProfileUpdate, CoachProfileResponse,
    SpecialtyCreate, SpecialtyResponse,
    CertificationCreate, CertificationResponse,
    PricingCreate, PricingUpdate, PricingResponse,
    AvailabilityCreate, AvailabilityResponse,
    CancellationPolicyUpdate, CancellationPolicyResponse,
)
from app.schemas.client import RelationStatusUpdate, RelationResponse, CoachNoteUpdate
from app.schemas.common import MessageResponse
from app.services import coach_service
from app.repositories import coach_repository
from app.services.coach_service import ProfileAlreadyExistsError, ProfileNotFoundError

router = APIRouter(prefix="/coaches", tags=["coaches"])


def _profile_not_found():
    return HTTPException(status_code=404, detail="Profil coach introuvable")


def _not_found(what: str = "Ressource"):
    return HTTPException(status_code=404, detail=f"{what} introuvable")


# ── Profil ─────────────────────────────────────────────────────────────────────

@router.post("/profile", response_model=CoachProfileResponse, status_code=201)
async def create_profile(
    data: CoachProfileCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        profile = await coach_service.create_profile(db, current_user, data)
        await db.commit()
        # Recharger avec les relations
        profile = await coach_repository.get_by_user_id(db, current_user.id)
        return profile
    except ProfileAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/profile", response_model=CoachProfileResponse)
async def get_profile(
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await coach_service.get_my_profile(db, current_user)
    except ProfileNotFoundError:
        raise _profile_not_found()


@router.put("/profile", response_model=CoachProfileResponse)
async def update_profile(
    data: CoachProfileUpdate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        await coach_service.update_profile(db, current_user, data)
        await db.commit()
        # Re-fetch avec relations (refresh() ne charge pas les relations lazy)
        profile = await coach_repository.get_by_user_id(db, current_user.id)
        return profile
    except ProfileNotFoundError:
        raise _profile_not_found()


# ── Spécialités ───────────────────────────────────────────────────────────────

@router.post("/profile/specialties", response_model=SpecialtyResponse, status_code=201)
async def add_specialty(
    data: SpecialtyCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    obj = await coach_repository.add_specialty(db, profile.id, data.specialty)
    await db.commit()
    return obj


@router.delete("/profile/specialties/{specialty_id}", response_model=MessageResponse)
async def remove_specialty(
    specialty_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    ok = await coach_repository.remove_specialty(db, profile.id, specialty_id)
    if not ok:
        raise _not_found("Spécialité")
    await db.commit()
    return {"message": "Spécialité supprimée"}


# ── Certifications ────────────────────────────────────────────────────────────

@router.post("/profile/certifications", response_model=CertificationResponse, status_code=201)
async def add_certification(
    data: CertificationCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    obj = await coach_repository.add_certification(db, profile.id, **data.model_dump())
    await db.commit()
    return obj


@router.delete("/profile/certifications/{cert_id}", response_model=MessageResponse)
async def remove_certification(
    cert_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    ok = await coach_repository.remove_certification(db, profile.id, cert_id)
    if not ok:
        raise _not_found("Certification")
    await db.commit()
    return {"message": "Certification supprimée"}


# ── Pricing ───────────────────────────────────────────────────────────────────

@router.post("/pricing", response_model=PricingResponse, status_code=201)
async def create_pricing(
    data: PricingCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    obj = await coach_repository.add_pricing(db, profile.id, **data.model_dump())
    await db.commit()
    return obj


@router.get("/pricing", response_model=list[PricingResponse])
async def list_pricing(
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id)
    if not profile:
        raise _profile_not_found()
    return profile.pricing


@router.put("/pricing/{pricing_id}", response_model=PricingResponse)
async def update_pricing(
    pricing_id: uuid.UUID,
    data: PricingUpdate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    obj = await coach_repository.get_pricing(db, profile.id, pricing_id)
    if not obj:
        raise _not_found("Tarif")
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    obj = await coach_repository.update_pricing(db, obj, **updates)
    await db.commit()
    return obj


@router.delete("/pricing/{pricing_id}", response_model=MessageResponse)
async def delete_pricing(
    pricing_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    obj = await coach_repository.get_pricing(db, profile.id, pricing_id)
    if not obj:
        raise _not_found("Tarif")
    await coach_repository.delete_pricing(db, obj)
    await db.commit()
    return {"message": "Tarif supprimé"}


# ── Disponibilités ────────────────────────────────────────────────────────────

@router.post("/availability", response_model=AvailabilityResponse, status_code=201)
async def add_availability(
    data: AvailabilityCreate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    obj = await coach_repository.add_availability(db, profile.id, **data.model_dump())
    await db.commit()
    return obj


@router.get("/availability", response_model=list[AvailabilityResponse])
async def list_availability(
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id)
    if not profile:
        raise _profile_not_found()
    return profile.availability


@router.delete("/availability/{avail_id}", response_model=MessageResponse)
async def delete_availability(
    avail_id: uuid.UUID,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    profile = await coach_repository.get_by_user_id(db, current_user.id, load_relations=False)
    if not profile:
        raise _profile_not_found()
    obj = await coach_repository.get_availability(db, profile.id, avail_id)
    if not obj:
        raise _not_found("Créneau")
    await coach_repository.delete_availability(db, obj)
    await db.commit()
    return {"message": "Créneau supprimé"}


# ── Politique d'annulation ────────────────────────────────────────────────────

@router.put("/cancellation-policy", response_model=CancellationPolicyResponse)
async def set_cancellation_policy(
    data: CancellationPolicyUpdate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        policy = await coach_service.set_cancellation_policy(db, current_user, data)
        await db.commit()
        return policy
    except ProfileNotFoundError:
        raise _profile_not_found()


# ── Clients ────────────────────────────────────────────────────────────────────

@router.get("/clients")
async def list_clients(
    status: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await coach_service.list_clients(
            db, current_user, status=status, offset=offset, limit=limit
        )
    except ProfileNotFoundError:
        raise _profile_not_found()


@router.put("/clients/{client_id}/relation", response_model=RelationResponse)
async def update_relation(
    client_id: uuid.UUID,
    data: RelationStatusUpdate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    rel = await coach_service.update_client_relation(db, current_user, client_id, data.status)
    await db.commit()
    return rel


@router.put("/clients/{client_id}/note", response_model=MessageResponse)
async def update_note(
    client_id: uuid.UUID,
    data: CoachNoteUpdate,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    await coach_service.update_note(db, current_user, client_id, data.content)
    await db.commit()
    return {"message": "Note mise à jour"}

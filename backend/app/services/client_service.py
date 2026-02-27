"""Service client — B2-13."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.client_profile import ClientProfile
from app.models.coaching_request import CoachingRequest
from app.repositories import client_repository, coach_repository
from app.schemas.client import ClientProfileCreate, ClientProfileUpdate, QuestionnaireCreate


class ProfileAlreadyExistsError(Exception):
    pass


class ProfileNotFoundError(Exception):
    pass


class CoachNotFoundError(Exception):
    pass


# ── Profil client ──────────────────────────────────────────────────────────────

async def create_profile(
    db: AsyncSession, user: User, data: ClientProfileCreate
) -> ClientProfile:
    existing = await client_repository.get_profile_by_user_id(db, user.id)
    if existing:
        raise ProfileAlreadyExistsError("Un profil client existe déjà")
    # Un coach a toutes les fonctionnalités client — il peut aussi créer un profil client.
    # Seuls les admins sont exclus.
    if user.role not in ("client", "coach"):
        from app.services.coach_service import NotAuthorizedError
        raise NotAuthorizedError("Les administrateurs ne peuvent pas créer un profil client")

    profile = await client_repository.create_profile(db, user.id, **data.model_dump())
    return profile


async def get_my_profile(db: AsyncSession, user: User) -> ClientProfile:
    profile = await client_repository.get_profile_by_user_id(db, user.id)
    if profile is None:
        raise ProfileNotFoundError("Profil client introuvable")
    return profile


async def update_profile(
    db: AsyncSession, user: User, data: ClientProfileUpdate
) -> ClientProfile:
    profile = await client_repository.get_profile_by_user_id(db, user.id)
    if profile is None:
        raise ProfileNotFoundError("Profil client introuvable")
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    return await client_repository.update_profile(db, profile, **updates)


# ── Questionnaire ──────────────────────────────────────────────────────────────

async def upsert_questionnaire(
    db: AsyncSession, user: User, data: QuestionnaireCreate
):
    return await client_repository.upsert_questionnaire(db, user.id, **data.model_dump())


# ── Recherche de coaches ──────────────────────────────────────────────────────

async def search_coaches(
    db: AsyncSession,
    *,
    country: str | None = None,
    specialty: str | None = None,
    discovery_only: bool = False,
    offset: int = 0,
    limit: int = 50,
):
    """Recherche de coaches publics (discovery_enabled=True)."""
    from app.models.coach_profile import CoachProfile
    q = select(CoachProfile).where(
        CoachProfile.discovery_enabled.is_(True),
        CoachProfile.verified.is_(True),
    )
    if country:
        q = q.where(CoachProfile.country == country.upper())
    q = q.offset(offset).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


# ── Demandes de coaching ──────────────────────────────────────────────────────

async def send_discovery_request(
    db: AsyncSession,
    client: User,
    coach_id: uuid.UUID,
    client_message: str | None = None,
    discovery_slot=None,
) -> CoachingRequest:
    coach_profile = await coach_repository.get_by_id(db, coach_id, load_relations=False)
    if coach_profile is None:
        raise CoachNotFoundError("Coach introuvable")

    req = CoachingRequest(
        id=uuid.uuid4(),
        client_id=client.id,
        coach_id=coach_profile.user_id,
        status="pending",
        client_message=client_message,
        discovery_slot=discovery_slot,
    )
    db.add(req)
    await db.flush()
    return req

"""Service coach — B1-23."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.coach_profile import CoachProfile
from app.repositories import coach_repository, cancellation_template_repository
from app.schemas.coach import (
    CoachProfileCreate,
    CoachProfileUpdate,
    CancellationPolicyUpdate,
)


class ProfileAlreadyExistsError(Exception):
    pass


class ProfileNotFoundError(Exception):
    pass


class NotAuthorizedError(Exception):
    pass


# ── Profil ─────────────────────────────────────────────────────────────────────

async def create_profile(
    db: AsyncSession, user: User, data: CoachProfileCreate
) -> CoachProfile:
    existing = await coach_repository.get_by_user_id(db, user.id, load_relations=False)
    if existing:
        raise ProfileAlreadyExistsError("Un profil coach existe déjà pour cet utilisateur")
    if user.role != "coach":
        raise NotAuthorizedError("Seuls les utilisateurs avec le rôle 'coach' peuvent créer un profil coach")

    profile = await coach_repository.create_profile(db, user.id, **data.model_dump())

    # Seed : créer le template d'annulation par défaut (B1-29)
    await cancellation_template_repository.create_default(db, profile.id)

    return profile


async def get_my_profile(db: AsyncSession, user: User) -> CoachProfile:
    profile = await coach_repository.get_by_user_id(db, user.id)
    if profile is None:
        raise ProfileNotFoundError("Profil coach introuvable")
    return profile


async def update_profile(
    db: AsyncSession, user: User, data: CoachProfileUpdate
) -> CoachProfile:
    profile = await coach_repository.get_by_user_id(db, user.id, load_relations=False)
    if profile is None:
        raise ProfileNotFoundError("Profil coach introuvable")
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    return await coach_repository.update_profile(db, profile, **updates)


async def get_public_profile(
    db: AsyncSession, profile_id: uuid.UUID
) -> CoachProfile:
    profile = await coach_repository.get_by_id(db, profile_id)
    if profile is None:
        raise ProfileNotFoundError("Profil coach introuvable")
    return profile


# ── Clients ────────────────────────────────────────────────────────────────────

async def list_clients(
    db: AsyncSession,
    user: User,
    *,
    status: str | None = None,
    offset: int = 0,
    limit: int = 50,
):
    profile = await coach_repository.get_by_user_id(db, user.id, load_relations=False)
    if profile is None:
        raise ProfileNotFoundError("Profil coach introuvable")
    return await coach_repository.get_clients(
        db, user.id, status=status, offset=offset, limit=limit
    )


async def update_client_relation(
    db: AsyncSession, user: User, client_id: uuid.UUID, status: str
):
    return await coach_repository.upsert_relation(db, user.id, client_id, status)


async def update_note(
    db: AsyncSession, user: User, client_id: uuid.UUID, content: str | None
):
    note = await coach_repository.get_or_create_note(db, user.id, client_id)
    return await coach_repository.update_note(db, note, content)


# ── Politique d'annulation ─────────────────────────────────────────────────────

async def set_cancellation_policy(
    db: AsyncSession, user: User, data: CancellationPolicyUpdate
):
    profile = await coach_repository.get_by_user_id(db, user.id, load_relations=False)
    if profile is None:
        raise ProfileNotFoundError("Profil coach introuvable")
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    return await coach_repository.upsert_cancellation_policy(db, profile.id, **updates)

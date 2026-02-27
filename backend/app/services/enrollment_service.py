"""Service — liens d'enrôlement coach (Phase 9)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coach_enrollment_token import CoachEnrollmentToken
from app.models.coaching_relation import CoachingRelation
from app.repositories import enrollment_repository
from app.schemas.enrollment import EnrollmentTokenCreate


# ---------------------------------------------------------------------------
# Exceptions métier
# ---------------------------------------------------------------------------

class EnrollmentTokenNotFoundError(Exception):
    """Token introuvable."""
    pass


class EnrollmentTokenExpiredError(Exception):
    """Token expiré."""
    pass


class EnrollmentTokenExhaustedError(Exception):
    """Token épuisé (max_uses atteint)."""
    pass


class EnrollmentTokenInactiveError(Exception):
    """Token désactivé manuellement."""
    pass


# ---------------------------------------------------------------------------
# Deep link
# ---------------------------------------------------------------------------

DEEP_LINK_BASE = "mycoach://enroll/"


def build_enrollment_link(token: str) -> str:
    return f"{DEEP_LINK_BASE}{token}"


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

async def create_token(
    db: AsyncSession,
    coach_id: uuid.UUID,
    data: EnrollmentTokenCreate,
) -> CoachEnrollmentToken:
    """Crée un token d'enrôlement pour le coach."""
    return await enrollment_repository.create_token(db, coach_id, data)


async def list_tokens(
    db: AsyncSession,
    coach_id: uuid.UUID,
) -> list[CoachEnrollmentToken]:
    """Liste les tokens d'un coach."""
    return await enrollment_repository.list_by_coach(db, coach_id)


async def deactivate_token(
    db: AsyncSession,
    coach_id: uuid.UUID,
    token_id: uuid.UUID,
) -> None:
    """
    Désactive un token.

    Raises:
        EnrollmentTokenNotFoundError: si le token est introuvable ou n'appartient pas au coach.
    """
    token = await enrollment_repository.get_by_id(db, token_id, coach_id)
    if token is None:
        raise EnrollmentTokenNotFoundError(str(token_id))
    await enrollment_repository.deactivate(db, token)


async def validate_token(
    db: AsyncSession,
    token_str: str,
) -> CoachEnrollmentToken:
    """
    Valide le token et retourne l'objet.

    Raises:
        EnrollmentTokenNotFoundError: token introuvable.
        EnrollmentTokenInactiveError: token désactivé.
        EnrollmentTokenExpiredError: token expiré.
        EnrollmentTokenExhaustedError: token épuisé.
    """
    token = await enrollment_repository.get_by_token(db, token_str)
    if token is None:
        raise EnrollmentTokenNotFoundError("Token introuvable")
    if not token.active:
        raise EnrollmentTokenInactiveError("Token désactivé")
    if token.expires_at is not None:
        now = datetime.now(timezone.utc)
        # S'assurer que expires_at est timezone-aware pour la comparaison
        expires = token.expires_at
        if expires.tzinfo is None:
            from datetime import timezone as tz
            expires = expires.replace(tzinfo=timezone.utc)
        if now > expires:
            raise EnrollmentTokenExpiredError("Token expiré")
    if token.max_uses is not None and token.uses_count >= token.max_uses:
        raise EnrollmentTokenExhaustedError("Token épuisé")
    return token


async def get_coach_info_for_token(
    db: AsyncSession,
    token_str: str,
) -> dict:
    """
    Retourne les infos publiques du coach pour l'écran de pré-inscription.

    Raises:
        EnrollmentTokenNotFoundError / InactiveError / ExpiredError / ExhaustedError
    """
    token = await validate_token(db, token_str)

    # Charger le user (coach) avec son profil
    from app.models.user import User
    from app.models.coach_profile import CoachProfile
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(User)
        .options(selectinload(User.coach_profile))
        .where(User.id == token.coach_id)
    )
    coach = result.scalar_one_or_none()

    bio = None
    avatar_url = None
    if coach is not None:
        avatar_url = coach.avatar_url
        if coach.coach_profile is not None:
            bio = coach.coach_profile.bio

    return {
        "coach_id": token.coach_id,
        "coach_first_name": coach.first_name if coach else "",
        "coach_last_name": coach.last_name if coach else "",
        "coach_bio": bio,
        "coach_avatar_url": avatar_url,
        "label": token.label,
        "valid": True,
    }


async def consume_token(
    db: AsyncSession,
    token: CoachEnrollmentToken,
    new_client_id: uuid.UUID,
) -> None:
    """
    Consomme le token :
    - Incrémente uses_count
    - Désactive si max_uses atteint
    - Crée la coaching_relation entre coach et client (si elle n'existe pas déjà)
    """
    await enrollment_repository.increment_uses(db, token)

    if token.max_uses is not None and token.uses_count >= token.max_uses:
        await enrollment_repository.deactivate(db, token)

    # Vérifier si la relation existe déjà
    result = await db.execute(
        select(CoachingRelation).where(
            CoachingRelation.coach_id == token.coach_id,
            CoachingRelation.client_id == new_client_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing is None:
        relation = CoachingRelation(
            coach_id=token.coach_id,
            client_id=new_client_id,
            status="active",
        )
        db.add(relation)
        await db.flush()

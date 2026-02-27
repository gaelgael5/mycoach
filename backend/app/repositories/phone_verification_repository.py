"""Repository — PhoneVerificationToken."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.phone_verification_token import PhoneVerificationToken


async def create_token(
    db: AsyncSession,
    user_id: uuid.UUID,
    phone: str,
    code: str,
    expires_at: datetime,
) -> PhoneVerificationToken:
    """Crée et persiste un nouveau token OTP."""
    token = PhoneVerificationToken(
        id=uuid.uuid4(),
        user_id=user_id,
        phone=phone,
        code=code,
        expires_at=expires_at,
        attempts_count=0,
    )
    db.add(token)
    await db.flush()
    return token


async def get_latest_for_user(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> PhoneVerificationToken | None:
    """
    Retourne le token OTP le plus récent pour cet utilisateur,
    qu'il soit expiré ou non, vérifié ou non.
    """
    result = await db.execute(
        select(PhoneVerificationToken)
        .where(PhoneVerificationToken.user_id == user_id)
        .where(PhoneVerificationToken.verified_at.is_(None))
        .order_by(PhoneVerificationToken.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_valid_for_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    code: str,
) -> PhoneVerificationToken | None:
    """
    Retourne un token valide : code correct + non expiré + attempts_count < 3.
    Retourne None si aucun token ne correspond.
    """
    now = datetime.now(timezone.utc)
    from app.utils.otp import OTP_MAX_ATTEMPTS
    result = await db.execute(
        select(PhoneVerificationToken)
        .where(PhoneVerificationToken.user_id == user_id)
        .where(PhoneVerificationToken.code == code)
        .where(PhoneVerificationToken.expires_at > now)
        .where(PhoneVerificationToken.verified_at.is_(None))
        .where(PhoneVerificationToken.attempts_count < OTP_MAX_ATTEMPTS)
        .order_by(PhoneVerificationToken.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def increment_attempts(
    db: AsyncSession,
    token: PhoneVerificationToken,
) -> None:
    """Incrémente le compteur de tentatives d'un token."""
    token.attempts_count += 1
    await db.flush()


async def mark_verified(
    db: AsyncSession,
    token: PhoneVerificationToken,
) -> None:
    """Marque le token comme vérifié (verified_at = now)."""
    token.verified_at = datetime.now(timezone.utc)
    await db.flush()


async def count_sent_last_hour(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    """Compte le nombre d'OTPs créés dans la dernière heure pour cet utilisateur."""
    since = datetime.now(timezone.utc) - timedelta(hours=1)
    result = await db.execute(
        select(func.count())
        .select_from(PhoneVerificationToken)
        .where(PhoneVerificationToken.user_id == user_id)
        .where(PhoneVerificationToken.created_at >= since)
    )
    return result.scalar_one()

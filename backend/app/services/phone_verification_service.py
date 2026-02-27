"""Service — Vérification du numéro de téléphone par OTP SMS."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories import phone_verification_repository
from app.utils.otp import (
    OTP_EXPIRY_MINUTES,
    OTP_MAX_ATTEMPTS,
    OTP_RATE_LIMIT_HOUR,
    format_sms,
    generate_otp,
)


# ---------------------------------------------------------------------------
# Exceptions métier
# ---------------------------------------------------------------------------

class PhoneAlreadyVerifiedError(Exception):
    """Le numéro de téléphone est déjà vérifié."""


class PhoneVerificationRateLimitError(Exception):
    """Trop de demandes d'OTP dans la dernière heure."""


class InvalidOtpError(Exception):
    """Code OTP invalide ou expiré."""


class OtpExpiredError(Exception):
    """Code OTP expiré."""


class OtpMaxAttemptsError(Exception):
    """Nombre maximum de tentatives atteint pour ce code."""


# ---------------------------------------------------------------------------
# Fonctions de service
# ---------------------------------------------------------------------------

async def request_phone_verification(db: AsyncSession, user: User) -> None:
    """
    Envoie un OTP SMS à l'utilisateur.

    - Vérifie que le téléphone n'est pas déjà vérifié
    - Rate limit : max OTP_RATE_LIMIT_HOUR OTPs par heure
    - Génère OTP, enregistre en DB, envoie SMS
    """
    if user.phone_verified_at is not None:
        raise PhoneAlreadyVerifiedError("Numéro de téléphone déjà vérifié")

    if user.phone is None:
        raise ValueError("Numéro de téléphone manquant")

    # Rate limit
    count = await phone_verification_repository.count_sent_last_hour(db, user.id)
    if count >= OTP_RATE_LIMIT_HOUR:
        raise PhoneVerificationRateLimitError("Trop de demandes. Réessayez dans une heure.")

    code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
    await phone_verification_repository.create_token(db, user.id, user.phone, code, expires_at)

    from app.core.sms.provider import get_sms_provider
    sms = get_sms_provider()
    await sms.send(user.phone, format_sms(code))


async def confirm_phone_verification(db: AsyncSession, user: User, code: str) -> None:
    """
    Valide l'OTP saisi par l'utilisateur.
    Met à jour phone_verified_at sur le User si le code est correct.
    """
    token = await phone_verification_repository.get_valid_for_user(db, user.id, code)

    if token is None:
        # Chercher le dernier token pour incrémenter les tentatives
        latest = await phone_verification_repository.get_latest_for_user(db, user.id)
        if latest and latest.attempts_count >= OTP_MAX_ATTEMPTS - 1:
            await phone_verification_repository.increment_attempts(db, latest)
            raise OtpMaxAttemptsError(
                "Code invalide. Trop de tentatives. Demandez un nouveau code."
            )
        if latest:
            await phone_verification_repository.increment_attempts(db, latest)
        raise InvalidOtpError("Code invalide ou expiré")

    await phone_verification_repository.mark_verified(db, token)
    user.phone_verified_at = datetime.now(timezone.utc)
    await db.flush()

"""Router — Vérification du numéro de téléphone par OTP SMS."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.phone_verification_service import (
    InvalidOtpError,
    OtpExpiredError,
    OtpMaxAttemptsError,
    PhoneAlreadyVerifiedError,
    PhoneVerificationRateLimitError,
    confirm_phone_verification,
    request_phone_verification,
)

router = APIRouter(prefix="/auth", tags=["phone-verification"])


class PhoneVerificationConfirm(BaseModel):
    code: str


@router.post("/verify-phone/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Envoie un OTP SMS au numéro de l'utilisateur connecté."""
    try:
        await request_phone_verification(db, current_user)
        await db.commit()
    except PhoneAlreadyVerifiedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PhoneVerificationRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-phone/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_verification(
    data: PhoneVerificationConfirm,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Valide le code OTP reçu par SMS."""
    try:
        await confirm_phone_verification(db, current_user, data.code)
        await db.commit()
    except (InvalidOtpError, OtpExpiredError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OtpMaxAttemptsError as e:
        raise HTTPException(status_code=400, detail=str(e))

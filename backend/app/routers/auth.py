"""
Router /auth — endpoints publics (pas de middleware API Key).
Toutes les réponses d'erreur utilisent les clés i18n.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    MeResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
)
from app.services.auth_service import (
    AccountNotVerifiedError,
    AccountSuspendedError,
    AuthService,
    EmailAlreadyUsedError,
    GoogleAuthError,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    auth_service,
)
from app.utils.hashing import hash_api_key
from app.utils.i18n import get_locale_from_request, t

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    locale = get_locale_from_request(request)
    try:
        result = await auth_service.register(
            db,
            first_name=body.first_name,
            last_name=body.last_name,
            email=str(body.email),
            password=body.password,
            role=body.role,
            device_label=body.device_label,
        )
        await db.commit()
        return AuthResponse(
            api_key=result.api_key,
            user=UserResponse.from_user(result.user),
        )
    except EmailAlreadyUsedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=t("auth.error.email_already_used", locale),
        )


# ---------------------------------------------------------------------------
# GET /auth/verify-email?token=...
# ---------------------------------------------------------------------------

@router.get("/verify-email")
async def verify_email(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    locale = get_locale_from_request(request)
    try:
        await auth_service.verify_email(db, token)
        await db.commit()
        return {"detail": t("auth.success.email_verified", locale)}
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("auth.error.token_invalid", locale),
        )
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("auth.error.token_expired", locale),
        )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    locale = get_locale_from_request(request)
    try:
        result = await auth_service.login_with_email(
            db,
            email=str(body.email),
            password=body.password,
            device_label=body.device_label,
        )
        await db.commit()
        return AuthResponse(
            api_key=result.api_key,
            user=UserResponse.from_user(result.user),
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("auth.error.invalid_credentials", locale),
        )
    except AccountNotVerifiedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=t("auth.error.account_not_verified", locale),
        )
    except AccountSuspendedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=t("auth.error.account_suspended", locale),
        )


# ---------------------------------------------------------------------------
# POST /auth/google
# ---------------------------------------------------------------------------

@router.post("/google", response_model=AuthResponse)
async def login_google(
    body: GoogleLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    locale = get_locale_from_request(request)
    try:
        result, is_new = await auth_service.login_with_google(
            db,
            id_token=body.id_token,
            device_label=body.device_label,
        )
        await db.commit()
        response = AuthResponse(
            api_key=result.api_key,
            user=UserResponse.from_user(result.user),
        )
        # L'app Android détecte is_new via profile_completion_pct == 0
        return response
    except GoogleAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("auth.error.google_token_invalid", locale),
        )


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=MeResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Vérifie que la clé est valide et retourne le profil courant."""
    return MeResponse(user=UserResponse.from_user(current_user))


# ---------------------------------------------------------------------------
# DELETE /auth/logout
# ---------------------------------------------------------------------------

@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Révoque la clé courante."""
    plain_key = request.headers.get("X-API-Key", "")
    await auth_service.logout(db, plain_key)
    await db.commit()


# ---------------------------------------------------------------------------
# DELETE /auth/logout-all
# ---------------------------------------------------------------------------

@router.delete("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Révoque toutes les clés de l'utilisateur (tous appareils)."""
    await auth_service.logout_all(db, current_user.id)
    await db.commit()


# ---------------------------------------------------------------------------
# POST /auth/forgot-password
# ---------------------------------------------------------------------------

@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Envoie un lien de reset si l'email existe.
    Réponse identique que l'email existe ou non (sécurité).
    """
    locale = get_locale_from_request(request)
    await auth_service.forgot_password(db, str(body.email))
    await db.commit()
    return {"detail": t("auth.success.password_reset_sent", locale)}


# ---------------------------------------------------------------------------
# POST /auth/reset-password
# ---------------------------------------------------------------------------

@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    locale = get_locale_from_request(request)
    try:
        await auth_service.reset_password(db, body.token, body.new_password)
        await db.commit()
        return {"detail": t("auth.success.password_reset_done", locale)}
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("auth.error.token_invalid", locale),
        )
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("auth.error.token_expired", locale),
        )

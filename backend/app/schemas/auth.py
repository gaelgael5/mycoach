"""
Schemas Pydantic — Authentification.
Toutes les validations métier (longueur, format, règles password) sont ici.
"""
import re
import uuid
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Validators réutilisables
# ---------------------------------------------------------------------------

def _validate_password(v: str) -> str:
    """
    Min 8 chars, au moins 1 majuscule, au moins 1 chiffre.
    Règle définie dans FUNCTIONAL_SPECS_DETAILED.md §1.1.
    """
    if len(v) < 8:
        raise ValueError("password_too_short")
    if not any(c.isupper() for c in v):
        raise ValueError("password_needs_uppercase")
    if not any(c.isdigit() for c in v):
        raise ValueError("password_needs_digit")
    return v


def _validate_name(v: str) -> str:
    """Min 2 chars, max 150 chars (noms internationaux)."""
    v = v.strip()
    if len(v) < 2:
        raise ValueError("name_too_short")
    if len(v) > 150:
        raise ValueError("name_too_long")
    return v


# ---------------------------------------------------------------------------
# Requêtes
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Inscription coach ou client — étape 1 (seule étape bloquante)."""

    first_name: Annotated[str, Field(min_length=2, max_length=150)]
    last_name: Annotated[str, Field(min_length=2, max_length=150)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]
    confirm_password: str
    role: str = Field(pattern="^(coach|client)$")
    device_label: str | None = Field(default=None, max_length=100)
    enrollment_token: Optional[str] = None
    gender: Optional[str] = None   # 'male' | 'female' | 'other'
    birth_year: Optional[int] = None  # ex: 1990

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return _validate_name(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("passwords_do_not_match")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_label: str | None = Field(default=None, max_length=100)


class GoogleLoginRequest(BaseModel):
    """Google ID token obtenu côté Android via le SDK Google Sign-In."""

    id_token: str
    device_label: str | None = Field(default=None, max_length=100)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str  # token en clair (SHA-256 vérifié côté service)
    new_password: Annotated[str, Field(min_length=8, max_length=128)]
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password(v)

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("passwords_do_not_match")
        return self


class LogoutAllRequest(BaseModel):
    """Optionnel — contexte de confirmation côté client."""
    reason: str | None = None


# ---------------------------------------------------------------------------
# Réponses
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """Données utilisateur retournées dans les réponses API."""

    id: uuid.UUID
    role: str
    status: str
    first_name: str
    last_name: str
    # email NON retourné par défaut (sécurité — le client le connaît déjà)
    avatar_url: str | None
    locale: str
    timezone: str
    country: str
    profile_completion_pct: int
    email_verified: bool
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    resolved_avatar_url: str
    phone_verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_user(cls, user) -> "UserResponse":
        from app.schemas.common import resolve_avatar_url
        return cls(
            id=user.id,
            role=user.role,
            status=user.status,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            locale=user.locale,
            timezone=user.timezone,
            country=user.country,
            profile_completion_pct=user.profile_completion_pct,
            email_verified=user.email_verified_at is not None,
            gender=user.gender,
            birth_year=user.birth_year,
            resolved_avatar_url=resolve_avatar_url(user.avatar_url, user.gender),
            phone_verified=user.phone_verified_at is not None,
            created_at=user.created_at,
        )


class AuthResponse(BaseModel):
    """
    Réponse à la connexion réussie.
    api_key est retournée UNE SEULE FOIS — le client doit la stocker dans
    EncryptedSharedPreferences (Android) immédiatement.
    """

    api_key: str   # clé en clair — jamais loguée, jamais stockée côté serveur
    user: UserResponse


class MeResponse(BaseModel):
    """Réponse à GET /auth/me — vérifie que la clé est toujours valide."""

    user: UserResponse

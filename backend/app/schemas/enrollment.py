"""Schemas Pydantic — Liens d'enrôlement coach (Phase 9)."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class EnrollmentTokenCreate(BaseModel):
    label: Optional[str] = None         # max 100 chars
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None       # if set, must be >= 1

    @field_validator("label")
    @classmethod
    def label_max(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 100:
            raise ValueError("Label max 100 caractères")
        return v

    @field_validator("max_uses")
    @classmethod
    def max_uses_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError("max_uses doit être >= 1")
        return v


class EnrollmentTokenResponse(BaseModel):
    id: uuid.UUID
    token: str
    label: Optional[str]
    expires_at: Optional[datetime]
    max_uses: Optional[int]
    uses_count: int
    active: bool
    created_at: datetime
    # Lien deep link pour partage
    enrollment_link: str  # ex: "mycoach://enroll/{token}"

    model_config = {"from_attributes": True}


class EnrollmentTokenPublicInfo(BaseModel):
    """Infos publiques du coach pour l'écran de pré-inscription (via token)."""

    coach_id: uuid.UUID
    coach_first_name: str
    coach_last_name: str
    coach_bio: Optional[str]
    coach_avatar_url: Optional[str]
    label: Optional[str]    # libellé du lien
    valid: bool             # token actif, non expiré, uses < max_uses

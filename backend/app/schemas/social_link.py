"""Schémas Pydantic — Liens réseaux sociaux (Phase 7)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

VALID_PLATFORMS = [
    "instagram",
    "tiktok",
    "youtube",
    "linkedin",
    "x",
    "facebook",
    "strava",
    "website",
]


class SocialLinkCreate(BaseModel):
    platform: str
    url: str

    @field_validator("platform")
    @classmethod
    def platform_must_be_valid(cls, v: str) -> str:
        if v not in VALID_PLATFORMS:
            raise ValueError(
                f"Plateforme invalide. Valeurs acceptées : {', '.join(VALID_PLATFORMS)}"
            )
        return v

    @field_validator("url")
    @classmethod
    def url_must_be_http(cls, v: str) -> str:
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        if len(v) > 500:
            raise ValueError("L'URL ne peut pas dépasser 500 caractères")
        return v


class SocialLinkResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    platform: str
    url: str
    created_at: datetime

    model_config = {"from_attributes": True}

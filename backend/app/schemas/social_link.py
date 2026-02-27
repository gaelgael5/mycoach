"""Schémas Pydantic — Liens réseaux sociaux (Phase 7)."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

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

VALID_VISIBILITY = ["public", "coaches_only"]

MAX_LINKS_PER_USER = 20


class SocialLinkCreate(BaseModel):
    """Créer ou remplacer un lien réseau social.

    - platform standard (instagram, tiktok…) → UPSERT, label optionnel
    - platform=None → lien custom, label OBLIGATOIRE
    """

    platform: Optional[str] = None
    label: Optional[str] = None
    url: str
    visibility: str = "public"
    position: int = 0

    @field_validator("platform")
    @classmethod
    def platform_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PLATFORMS:
            raise ValueError(
                f"Plateforme invalide. Valeurs acceptées : {', '.join(VALID_PLATFORMS)} ou null pour un lien personnalisé"
            )
        return v

    @field_validator("label")
    @classmethod
    def label_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 100:
            raise ValueError("Le label ne peut pas dépasser 100 caractères")
        return v

    @field_validator("url")
    @classmethod
    def url_must_be_http(cls, v: str) -> str:
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        if len(v) > 500:
            raise ValueError("L'URL ne peut pas dépasser 500 caractères")
        return v

    @field_validator("visibility")
    @classmethod
    def visibility_must_be_valid(cls, v: str) -> str:
        if v not in VALID_VISIBILITY:
            raise ValueError(
                f"Visibilité invalide. Valeurs acceptées : {', '.join(VALID_VISIBILITY)}"
            )
        return v

    @model_validator(mode="after")
    def label_required_for_custom(self) -> "SocialLinkCreate":
        if self.platform is None and not self.label:
            raise ValueError(
                "Le champ 'label' est obligatoire pour un lien personnalisé (platform=null)"
            )
        return self


class SocialLinkUpdate(BaseModel):
    """Mettre à jour un lien existant (par son ID)."""

    label: Optional[str] = None
    url: Optional[str] = None
    visibility: Optional[str] = None
    position: Optional[int] = None

    @field_validator("url")
    @classmethod
    def url_must_be_http(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.startswith("http://") and not v.startswith("https://"):
                raise ValueError("L'URL doit commencer par http:// ou https://")
            if len(v) > 500:
                raise ValueError("L'URL ne peut pas dépasser 500 caractères")
        return v

    @field_validator("visibility")
    @classmethod
    def visibility_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_VISIBILITY:
            raise ValueError(
                f"Visibilité invalide. Valeurs acceptées : {', '.join(VALID_VISIBILITY)}"
            )
        return v

    @field_validator("label")
    @classmethod
    def label_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 100:
            raise ValueError("Le label ne peut pas dépasser 100 caractères")
        return v


class SocialLinkResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    platform: Optional[str]
    label: Optional[str]
    url: str
    visibility: str
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

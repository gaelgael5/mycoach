"""Schemas Pydantic — Coach (B1-17)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.models.coach_specialty import SPECIALTY_VALUES
from app.models.coach_pricing import PRICING_TYPES


# ── Spécialités ───────────────────────────────────────────────────────────────

class SpecialtyCreate(BaseModel):
    specialty: str

    @field_validator("specialty")
    @classmethod
    def validate_specialty(cls, v: str) -> str:
        if v not in SPECIALTY_VALUES:
            raise ValueError(f"Spécialité invalide. Valeurs : {SPECIALTY_VALUES}")
        return v


class SpecialtyResponse(BaseModel):
    id: uuid.UUID
    specialty: str

    model_config = {"from_attributes": True}


# ── Certifications ────────────────────────────────────────────────────────────

class CertificationCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=150)]
    organization: Annotated[str | None, Field(max_length=150)] = None
    year: Annotated[int | None, Field(ge=1950, le=2100)] = None
    document_url: str | None = None


class CertificationResponse(BaseModel):
    id: uuid.UUID
    name: str
    organization: str | None
    year: int | None
    document_url: str | None
    verified: bool

    model_config = {"from_attributes": True}


# ── Pricing ───────────────────────────────────────────────────────────────────

class PricingCreate(BaseModel):
    type: str
    name: Annotated[str, Field(min_length=2, max_length=100)]
    session_count: Annotated[int, Field(ge=1, le=200)] = 1
    price_cents: Annotated[int, Field(ge=0)]
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "EUR"
    validity_months: Annotated[int | None, Field(ge=1, le=24)] = None
    is_public: bool = True

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in PRICING_TYPES:
            raise ValueError(f"Type de tarif invalide. Valeurs : {PRICING_TYPES}")
        return v


class PricingUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=2, max_length=100)] = None
    price_cents: Annotated[int | None, Field(ge=0)] = None
    validity_months: Annotated[int | None, Field(ge=1, le=24)] = None
    is_public: bool | None = None


class PricingResponse(BaseModel):
    id: uuid.UUID
    type: str
    name: str
    session_count: int
    price_cents: int
    currency: str
    validity_months: int | None
    is_public: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Disponibilités ────────────────────────────────────────────────────────────

class AvailabilityCreate(BaseModel):
    day_of_week: Annotated[int, Field(ge=0, le=6)]
    start_time: str  # "HH:MM"
    end_time: str    # "HH:MM"
    max_slots: Annotated[int, Field(ge=1, le=50)] = 1
    booking_horizon_days: Annotated[int, Field(ge=1, le=365)] = 30

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        import re
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("Format HH:MM requis")
        return v


class AvailabilityResponse(BaseModel):
    id: uuid.UUID
    day_of_week: int
    start_time: str
    end_time: str
    max_slots: int
    booking_horizon_days: int
    active: bool

    model_config = {"from_attributes": True}

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def coerce_time_to_str(cls, v: object) -> str:
        """Convertit datetime.time → 'HH:MM' (asyncpg retourne des time objects)."""
        if hasattr(v, "hour"):
            return f"{v.hour:02d}:{v.minute:02d}"  # type: ignore[union-attr]
        return str(v)


# ── Politique d'annulation ────────────────────────────────────────────────────

class CancellationPolicyUpdate(BaseModel):
    threshold_hours: Annotated[int | None, Field(ge=1, le=168)] = None
    mode: str | None = None
    noshow_is_due: bool | None = None
    client_message: Annotated[str | None, Field(max_length=500)] = None

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in ("auto", "manual"):
            raise ValueError("mode doit être 'auto' ou 'manual'")
        return v


class CancellationPolicyResponse(BaseModel):
    id: uuid.UUID
    threshold_hours: int
    mode: str
    noshow_is_due: bool
    client_message: str | None

    model_config = {"from_attributes": True}


# ── Profil coach ──────────────────────────────────────────────────────────────

class CoachProfileCreate(BaseModel):
    bio: Annotated[str | None, Field(max_length=2000)] = None
    country: Annotated[str | None, Field(min_length=2, max_length=2)] = None
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "EUR"
    session_duration_min: Annotated[int, Field(ge=15, le=480)] = 60
    discovery_enabled: bool = False
    discovery_free: bool = True
    discovery_price_cents: Annotated[int | None, Field(ge=0)] = None
    booking_horizon_days: Annotated[int, Field(ge=1, le=365)] = 30
    sms_sender_name: Annotated[str | None, Field(max_length=11)] = None


class CoachProfileUpdate(BaseModel):
    bio: Annotated[str | None, Field(max_length=2000)] = None
    country: Annotated[str | None, Field(min_length=2, max_length=2)] = None
    currency: Annotated[str | None, Field(min_length=3, max_length=3)] = None
    session_duration_min: Annotated[int | None, Field(ge=15, le=480)] = None
    discovery_enabled: bool | None = None
    discovery_free: bool | None = None
    discovery_price_cents: Annotated[int | None, Field(ge=0)] = None
    booking_horizon_days: Annotated[int | None, Field(ge=1, le=365)] = None
    sms_sender_name: Annotated[str | None, Field(max_length=11)] = None


class CoachProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    bio: str | None
    verified: bool
    country: str | None
    currency: str
    session_duration_min: int
    discovery_enabled: bool
    discovery_free: bool
    discovery_price_cents: int | None
    booking_horizon_days: int
    sms_sender_name: str | None
    onboarding_completed: bool
    specialties: list[SpecialtyResponse] = []
    certifications: list[CertificationResponse] = []
    pricing: list[PricingResponse] = []
    cancellation_policy: CancellationPolicyResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

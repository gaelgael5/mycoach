"""Schemas Pydantic — Réservations, machine d'état, liste d'attente (B2-09)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.models.booking import BOOKING_STATUSES
from app.models.waitlist_entry import WAITLIST_STATUSES


# ── Réservations ───────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    """Création d'une réservation par un client."""
    coach_id: uuid.UUID
    scheduled_at: datetime  # UTC
    duration_min: Annotated[int, Field(ge=15, le=480)] = 60
    pricing_id: uuid.UUID | None = None
    package_id: uuid.UUID | None = None
    gym_id: uuid.UUID | None = None
    client_message: Annotated[str | None, Field(max_length=500)] = None


class BookingResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    coach_id: uuid.UUID
    pricing_id: uuid.UUID | None
    package_id: uuid.UUID | None
    gym_id: uuid.UUID | None
    scheduled_at: datetime
    duration_min: int
    status: str
    price_cents: int | None
    client_message: str | None
    coach_cancel_reason: str | None
    late_cancel_waived: bool
    confirmed_at: datetime | None
    cancelled_at: datetime | None
    done_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CancellationRequest(BaseModel):
    reason: Annotated[str | None, Field(max_length=500)] = None


class BookingListParams(BaseModel):
    status: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    offset: int = 0
    limit: int = 50


# ── Demandes de coaching ──────────────────────────────────────────────────────

class CoachingRequestCreate(BaseModel):
    coach_id: uuid.UUID
    client_message: Annotated[str | None, Field(max_length=1000)] = None
    discovery_slot: datetime | None = None


class CoachingRequestResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    coach_id: uuid.UUID
    status: str
    client_message: str | None
    coach_message: str | None
    discovery_slot: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CoachingRequestUpdate(BaseModel):
    status: str
    coach_message: Annotated[str | None, Field(max_length=1000)] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ("accepted", "rejected")
        if v not in allowed:
            raise ValueError(f"Statut invalide. Valeurs : {allowed}")
        return v


# ── Liste d'attente ────────────────────────────────────────────────────────────

class WaitlistJoinRequest(BaseModel):
    coach_id: uuid.UUID
    slot_datetime: datetime


class WaitlistEntryResponse(BaseModel):
    id: uuid.UUID
    coach_id: uuid.UUID
    slot_datetime: datetime
    client_id: uuid.UUID
    position: int
    status: str
    notified_at: datetime | None
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

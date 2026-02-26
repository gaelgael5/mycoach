"""Schemas Phase 5 — Intégrations OAuth + mesures corporelles."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


# ── OAuth Status ───────────────────────────────────────────────────────────────

class IntegrationStatus(BaseModel):
    provider: str
    connected: bool
    scope: str | None = None
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}


class AuthorizeResponse(BaseModel):
    authorize_url: str
    provider: str


class ConnectResponse(BaseModel):
    status: str
    provider: str
    scope: str | None = None


# ── Mesures corporelles ────────────────────────────────────────────────────────

class BodyMeasurementCreate(BaseModel):
    measured_at: datetime
    weight_kg: Annotated[Decimal | None, Field(ge=0, le=500)] = None
    fat_pct: Annotated[Decimal | None, Field(ge=0, le=100)] = None
    muscle_pct: Annotated[Decimal | None, Field(ge=0, le=100)] = None
    bone_kg: Annotated[Decimal | None, Field(ge=0, le=50)] = None
    water_pct: Annotated[Decimal | None, Field(ge=0, le=100)] = None
    bmi: Annotated[Decimal | None, Field(ge=0, le=100)] = None


class BodyMeasurementResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    measured_at: datetime
    weight_kg: Decimal | None
    bmi: Decimal | None
    fat_pct: Decimal | None
    muscle_pct: Decimal | None
    bone_kg: Decimal | None
    water_pct: Decimal | None
    source: str

    model_config = {"from_attributes": True}


# ── Push Strava ────────────────────────────────────────────────────────────────

class StravaActivityResponse(BaseModel):
    id: int | None = None
    name: str | None = None
    type: str | None = None
    start_date_local: str | None = None
    status: str = "pushed"

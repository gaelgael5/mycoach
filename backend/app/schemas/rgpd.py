"""Schemas RGPD — B6-02, B6-03, B6-04, B6-05."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator

from app.models.consent import CONSENT_TYPES


class ConsentCreate(BaseModel):
    consent_type: str
    version: str
    accepted: bool

    @field_validator("consent_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in CONSENT_TYPES:
            raise ValueError(f"Type invalide. Valeurs: {CONSENT_TYPES}")
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if len(v) > 20 or not v:
            raise ValueError("Version invalide (max 20 chars)")
        return v


class ConsentResponse(BaseModel):
    id: uuid.UUID
    consent_type: str
    version: str
    accepted: bool
    accepted_at: datetime

    model_config = {"from_attributes": True}


class ExportTokenResponse(BaseModel):
    token: str
    expires_in_hours: int = 24
    format: str = "json"


class DeletionResponse(BaseModel):
    message: str
    deletion_requested_at: datetime
    effective_at: str  # ISO date J+30


class UserExportData(BaseModel):
    export_date: str
    user: dict[str, Any]
    coach_profile: dict
    performance_sessions: list[dict]
    bookings: list[dict]
    payments: list[dict]
    body_measurements: list[dict]
    consents: list[dict]
    integrations_connected: list[str]

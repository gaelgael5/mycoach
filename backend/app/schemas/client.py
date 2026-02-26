"""Schemas Pydantic — Client (B1-18)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.models.client_profile import GOAL_VALUES, LEVEL_VALUES
from app.models.coaching_relation import RELATION_STATUSES


# ── Profil client ──────────────────────────────────────────────────────────────

class ClientProfileCreate(BaseModel):
    birth_date: str | None = None  # ISO "YYYY-MM-DD"
    weight_kg: Annotated[float | None, Field(ge=10, le=500)] = None
    height_cm: Annotated[int | None, Field(ge=50, le=300)] = None
    goal: str | None = None
    level: str | None = None
    weight_unit: str = "kg"
    country: Annotated[str | None, Field(min_length=2, max_length=2)] = None

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v: str | None) -> str | None:
        if v is not None and v not in GOAL_VALUES:
            raise ValueError(f"Objectif invalide. Valeurs : {GOAL_VALUES}")
        return v

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str | None) -> str | None:
        if v is not None and v not in LEVEL_VALUES:
            raise ValueError(f"Niveau invalide. Valeurs : {LEVEL_VALUES}")
        return v

    @field_validator("weight_unit")
    @classmethod
    def validate_weight_unit(cls, v: str) -> str:
        if v not in ("kg", "lb"):
            raise ValueError("weight_unit doit être 'kg' ou 'lb'")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: str | None) -> str | None:
        if v is None:
            return v
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("birth_date doit être au format YYYY-MM-DD")
        return v


class ClientProfileUpdate(ClientProfileCreate):
    pass


class ClientProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    birth_date: str | None  # déchiffré en clair dans la réponse
    weight_kg: float | None
    height_cm: int | None
    goal: str | None
    level: str | None
    weight_unit: str
    country: str | None
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Vues coach sur ses clients ────────────────────────────────────────────────

class ClientSummary(BaseModel):
    """Vue résumée d'un client dans la liste du coach."""
    user_id: uuid.UUID
    first_name: str  # déchiffré
    last_name: str   # déchiffré
    relation_status: str
    sessions_remaining: int | None  # from active package
    last_session_at: datetime | None

    model_config = {"from_attributes": True}


class ClientDetail(BaseModel):
    """Vue complète d'un client (coach uniquement)."""
    user_id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None  # masqué en production sauf consent
    phone: str | None
    relation_status: str
    profile: ClientProfileResponse | None
    note: str | None  # coach_client_notes.content déchiffré

    model_config = {"from_attributes": True}


# ── Relations ─────────────────────────────────────────────────────────────────

class RelationStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in RELATION_STATUSES:
            raise ValueError(f"Statut invalide. Valeurs : {RELATION_STATUSES}")
        return v


class RelationResponse(BaseModel):
    id: uuid.UUID
    coach_id: uuid.UUID
    client_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Notes coach ───────────────────────────────────────────────────────────────

class CoachNoteUpdate(BaseModel):
    content: Annotated[str | None, Field(max_length=5000)] = None

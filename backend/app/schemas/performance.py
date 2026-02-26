"""Schemas Phase 3 — Performances & Exercices — B3-09."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


# ── Exercise Sets ──────────────────────────────────────────────────────────────

class ExerciseSetCreate(BaseModel):
    exercise_type_id: uuid.UUID
    machine_id: uuid.UUID | None = None
    set_order: Annotated[int, Field(ge=1, le=50)] = 1
    sets_count: Annotated[int, Field(ge=1, le=20)] = 1
    reps: Annotated[int | None, Field(ge=0, le=9999)] = None
    weight_kg: Annotated[Decimal | None, Field(ge=0, le=9999)] = None
    notes: Annotated[str | None, Field(max_length=500)] = None


class ExerciseSetResponse(BaseModel):
    id: uuid.UUID
    exercise_type_id: uuid.UUID
    machine_id: uuid.UUID | None
    set_order: int
    sets_count: int
    reps: int | None
    weight_kg: Decimal | None
    notes: str | None
    is_pr: bool

    model_config = {"from_attributes": True}


# ── Performance Sessions ───────────────────────────────────────────────────────

class PerformanceSessionCreate(BaseModel):
    session_type: str = "solo_free"
    booking_id: uuid.UUID | None = None
    gym_id: uuid.UUID | None = None
    session_date: datetime
    duration_min: Annotated[int | None, Field(ge=1, le=600)] = None
    feeling: Annotated[int | None, Field(ge=1, le=5)] = None
    exercise_sets: list[ExerciseSetCreate] = Field(default_factory=list)

    @field_validator("session_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        from app.models.performance_session import SESSION_TYPES
        if v not in SESSION_TYPES:
            raise ValueError(f"session_type invalide. Valeurs : {SESSION_TYPES}")
        return v


class PerformanceSessionUpdate(BaseModel):
    session_date: datetime | None = None
    duration_min: Annotated[int | None, Field(ge=1, le=600)] = None
    feeling: Annotated[int | None, Field(ge=1, le=5)] = None
    exercise_sets: list[ExerciseSetCreate] | None = None


class PerformanceSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    session_type: str
    booking_id: uuid.UUID | None
    gym_id: uuid.UUID | None
    session_date: datetime
    duration_min: int | None
    feeling: int | None
    strava_activity_id: str | None
    created_at: datetime
    exercise_sets: list[ExerciseSetResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── Statistiques ───────────────────────────────────────────────────────────────

class ProgressionPoint(BaseModel):
    """Un point de progression (date + poids max + volume)."""
    session_date: datetime
    max_weight_kg: Decimal | None
    total_volume_kg: Decimal | None  # somme(reps * weight_kg) sur la séance
    sets_count: int


class ProgressionStats(BaseModel):
    exercise_type_id: uuid.UUID
    exercise_name_key: str
    data_points: list[ProgressionPoint]


class WeekStats(BaseModel):
    week_start: datetime
    sessions_count: int
    total_duration_min: int
    avg_feeling: float | None
    total_sets: int
    muscles_worked: list[str]


class PersonalRecordResponse(BaseModel):
    id: uuid.UUID
    exercise_type_id: uuid.UUID
    exercise_name_key: str
    weight_kg: Decimal
    reps: int | None
    achieved_at: datetime
    session_id: uuid.UUID

    model_config = {"from_attributes": True}


# ── Exercices ──────────────────────────────────────────────────────────────────

class ExerciseMuscleResponse(BaseModel):
    muscle_group: str
    role: str  # primary / secondary

    model_config = {"from_attributes": True}


class ExerciseTypeResponse(BaseModel):
    id: uuid.UUID
    name_key: str
    category: str
    difficulty: str
    video_url: str | None
    thumbnail_url: str | None
    instructions: list | None
    muscles: list[ExerciseMuscleResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── Machine ────────────────────────────────────────────────────────────────────

class MachineSubmit(BaseModel):
    type_key: str
    brand: Annotated[str | None, Field(max_length=100)] = None
    model_name: Annotated[str | None, Field(max_length=100)] = None
    qr_code_hash: Annotated[str | None, Field(max_length=64)] = None


class MachineResponse(BaseModel):
    id: uuid.UUID
    type_key: str
    brand: str | None
    model: str | None
    photo_url: str | None
    validated: bool

    model_config = {"from_attributes": True}

"""Schemas Phase 4 — Programmes d'entraînement — B4-09."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


# ── Exercices planifiés ────────────────────────────────────────────────────────

class PlannedExerciseCreate(BaseModel):
    exercise_type_id: uuid.UUID
    target_sets: Annotated[int, Field(ge=1, le=20)] = 3
    target_reps: Annotated[int, Field(ge=1, le=200)] = 10
    target_weight_kg: Annotated[Decimal | None, Field(ge=0)] = None
    order_index: Annotated[int, Field(ge=1)] = 1


class PlannedExerciseResponse(BaseModel):
    id: uuid.UUID
    exercise_type_id: uuid.UUID
    target_sets: int
    target_reps: int
    target_weight_kg: Decimal | None
    order_index: int

    model_config = {"from_attributes": True}


# ── Sessions planifiées ────────────────────────────────────────────────────────

class PlannedSessionCreate(BaseModel):
    day_of_week: Annotated[int, Field(ge=0, le=6)]
    session_name: Annotated[str, Field(min_length=2, max_length=100)]
    estimated_duration_min: Annotated[int | None, Field(ge=10, le=240)] = None
    rest_seconds: Annotated[int, Field(ge=30, le=300)] = 90
    planned_exercises: list[PlannedExerciseCreate] = Field(default_factory=list)


class PlannedSessionResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    day_of_week: int
    session_name: str
    estimated_duration_min: int | None
    rest_seconds: int
    order_index: int
    planned_exercises: list[PlannedExerciseResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── Plans ──────────────────────────────────────────────────────────────────────

class WorkoutPlanCreate(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=200)]
    description: Annotated[str | None, Field(max_length=1000)] = None
    duration_weeks: Annotated[int, Field(ge=1, le=52)] = 4
    level: str = "beginner"
    goal: str = "well_being"
    planned_sessions: list[PlannedSessionCreate] = Field(default_factory=list)

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        from app.models.workout_plan import PLAN_LEVELS
        if v not in PLAN_LEVELS:
            raise ValueError(f"level invalide. Valeurs : {PLAN_LEVELS}")
        return v

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v: str) -> str:
        from app.models.workout_plan import PLAN_GOALS
        if v not in PLAN_GOALS:
            raise ValueError(f"goal invalide. Valeurs : {PLAN_GOALS}")
        return v


class WorkoutPlanUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=2, max_length=200)] = None
    description: Annotated[str | None, Field(max_length=1000)] = None
    duration_weeks: Annotated[int | None, Field(ge=1, le=52)] = None


class WorkoutPlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    duration_weeks: int
    level: str
    goal: str
    is_ai_generated: bool
    archived: bool
    created_at: datetime
    planned_sessions: list[PlannedSessionResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class WorkoutPlanSummary(BaseModel):
    id: uuid.UUID
    name: str
    duration_weeks: int
    level: str
    goal: str
    is_ai_generated: bool
    archived: bool
    created_at: datetime
    sessions_count: int = 0

    model_config = {"from_attributes": True}


# ── Assignations ───────────────────────────────────────────────────────────────

class AssignPlanRequest(BaseModel):
    client_id: uuid.UUID
    start_date: date
    mode: str = "replace_ai"

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        from app.models.workout_plan import ASSIGN_MODES
        if v not in ASSIGN_MODES:
            raise ValueError(f"mode invalide. Valeurs : {ASSIGN_MODES}")
        return v


class PlanAssignmentResponse(BaseModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    client_id: uuid.UUID
    start_date: date
    mode: str
    active: bool
    created_at: datetime
    workout_plan: WorkoutPlanResponse | None = None

    model_config = {"from_attributes": True}


# ── Progression ────────────────────────────────────────────────────────────────

class ClientProgressResponse(BaseModel):
    plan_id: uuid.UUID
    planned_sessions: int
    completed_sessions: int
    completion_pct: float


# ── Génération IA ──────────────────────────────────────────────────────────────

class GenerateProgramRequest(BaseModel):
    goal: str = "well_being"
    frequency_per_week: Annotated[int, Field(ge=1, le=7)] = 3
    level: str = "beginner"

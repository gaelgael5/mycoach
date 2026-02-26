"""Modèles Phase 4 — Programmes d'entraînement — B4-01 à B4-05."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.exercise_type import ExerciseType


PLAN_LEVELS = ["beginner", "intermediate", "advanced"]
PLAN_GOALS = ["lose_weight", "muscle_gain", "endurance", "well_being", "maintenance", "rehab"]
ASSIGN_MODES = ["replace_ai", "complement"]
VIDEO_STATUSES = ["pending", "generating", "validating", "published", "rejected"]


# ── B4-01 — Plans d'entraînement ──────────────────────────────────────────────

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")
    goal: Mapped[str] = mapped_column(String(30), nullable=False, default="well_being")
    # NULL + is_ai_generated=True → programme IA généré (décision archi : pas de fake admin user)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relations
    planned_sessions: Mapped[list["PlannedSession"]] = relationship(
        "PlannedSession", back_populates="workout_plan", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["PlanAssignment"]] = relationship(
        "PlanAssignment", back_populates="workout_plan"
    )


# ── B4-02 — Assignation de plan à un client ────────────────────────────────────

class PlanAssignment(Base):
    __tablename__ = "plan_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False, default="replace_ai")
    assigned_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    workout_plan: Mapped["WorkoutPlan"] = relationship("WorkoutPlan", back_populates="assignments")


# ── B4-03 — Sessions planifiées (jours du plan) ────────────────────────────────

class PlannedSession(Base):
    __tablename__ = "planned_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Lundi … 6=Dimanche
    session_name: Mapped[str] = mapped_column(String(100), nullable=False)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rest_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    workout_plan: Mapped["WorkoutPlan"] = relationship(
        "WorkoutPlan", back_populates="planned_sessions"
    )
    planned_exercises: Mapped[list["PlannedExercise"]] = relationship(
        "PlannedExercise", back_populates="planned_session", cascade="all, delete-orphan"
    )


# ── B4-04 — Exercices planifiés ────────────────────────────────────────────────

class PlannedExercise(Base):
    __tablename__ = "planned_exercises"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planned_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("planned_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise_types.id", ondelete="RESTRICT"), nullable=False
    )
    target_sets: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    target_reps: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    target_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    planned_session: Mapped["PlannedSession"] = relationship(
        "PlannedSession", back_populates="planned_exercises"
    )
    exercise_type: Mapped["ExerciseType"] = relationship("ExerciseType")


# ── B4-05 — Vidéos d'exercices ────────────────────────────────────────────────

class ExerciseVideo(Base):
    __tablename__ = "exercise_videos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exercise_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise_types.id", ondelete="CASCADE"),
        nullable=False, unique=True  # 1-1
    )
    video_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    generated_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    exercise_type: Mapped["ExerciseType"] = relationship("ExerciseType")

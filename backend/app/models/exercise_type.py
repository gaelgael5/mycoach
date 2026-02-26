"""Modèle ExerciseType + MuscleGroup — B3-01."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.exercise_set import ExerciseSet


EXERCISE_CATEGORIES = [
    "strength", "cardio", "flexibility", "balance",
    "hiit", "yoga", "pilates", "rehab", "sport", "other",
]

EXERCISE_DIFFICULTIES = ["beginner", "intermediate", "advanced"]

MUSCLE_GROUPS = [
    "chest", "back", "shoulders", "biceps", "triceps", "forearms",
    "core", "glutes", "quads", "hamstrings", "calves",
    "hip_flexors", "adductors", "neck", "full_body",
]


class ExerciseType(Base):
    __tablename__ = "exercise_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Clé i18n : "exercise.squat", "exercise.bench_press", etc.
    name_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="strength")
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="intermediate")
    # Vidéo et miniature
    video_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Instructions étape par étape (texte libre ou liste i18n keys)
    instructions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relations
    muscles: Mapped[list["ExerciseTypeMuscle"]] = relationship(
        "ExerciseTypeMuscle", back_populates="exercise_type", cascade="all, delete-orphan"
    )
    exercise_sets: Mapped[list["ExerciseSet"]] = relationship(
        "ExerciseSet", back_populates="exercise_type"
    )


class ExerciseTypeMuscle(Base):
    """Table M-M entre ExerciseType et groupe musculaire (enum string)."""

    __tablename__ = "exercise_type_muscles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exercise_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercise_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    muscle_group: Mapped[str] = mapped_column(String(50), nullable=False)
    # primary = muscle principal, secondary = muscle secondaire
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="primary")

    exercise_type: Mapped["ExerciseType"] = relationship(
        "ExerciseType", back_populates="muscles"
    )

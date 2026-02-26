"""Modèle Machine + MachineExercise — B3-02, B3-03."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.exercise_type import ExerciseType
    from app.models.user import User


MACHINE_TYPES = [
    "cable", "smith", "leg_press", "chest_press", "lat_pulldown",
    "row", "shoulder_press", "leg_curl", "leg_extension",
    "hack_squat", "incline_press", "fly", "pull_up_assist",
    "dip_assist", "treadmill", "bike", "elliptical", "rowing",
    "free_weights", "barbell", "dumbbell", "other",
]


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    type_key: Mapped[str] = mapped_column(String(50), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # QR code hashé (SHA-256) pour scan rapide en salle
    qr_code_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    submitted_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    validated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    exercises: Mapped[list["MachineExercise"]] = relationship(
        "MachineExercise", back_populates="machine", cascade="all, delete-orphan"
    )


class MachineExercise(Base):
    """Relation M-M entre Machine et ExerciseType."""

    __tablename__ = "machine_exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercise_types.id", ondelete="CASCADE"),
        nullable=False,
    )

    machine: Mapped["Machine"] = relationship("Machine", back_populates="exercises")
    exercise_type: Mapped["ExerciseType"] = relationship("ExerciseType")

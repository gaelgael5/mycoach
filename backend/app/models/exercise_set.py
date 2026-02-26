"""Modèle ExerciseSet — B3-05.

Décision architecture (CODING_AGENT.md) :
- is_pr = TRUE pour les personal records — pas de table dédiée
- Index partiel `WHERE is_pr = TRUE` pour queryabilité rapide
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.exercise_type import ExerciseType
    from app.models.machine import Machine
    from app.models.performance_session import PerformanceSession


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("performance_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercise_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    machine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("machines.id", ondelete="SET NULL"),
        nullable=True,
    )

    set_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    sets_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Personal Record flag (décision archi : pas de table dédiée)
    is_pr: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relations
    performance_session: Mapped["PerformanceSession"] = relationship(
        "PerformanceSession", back_populates="exercise_sets"
    )
    exercise_type: Mapped["ExerciseType"] = relationship(
        "ExerciseType", back_populates="exercise_sets"
    )
    machine: Mapped["Machine | None"] = relationship("Machine")

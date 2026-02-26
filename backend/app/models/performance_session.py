"""Modèle PerformanceSession — B3-04."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.exercise_set import ExerciseSet
    from app.models.gym import Gym
    from app.models.user import User


SESSION_TYPES = ["solo_free", "solo_guided", "coached"]


class PerformanceSession(Base):
    __tablename__ = "performance_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Propriétaire de la session (client ou coach)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="solo_free"
    )
    # Séance de coaching associée (optionnel)
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Coach qui a saisi (optionnel — mode coached)
    entered_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Salle de sport associée (optionnel)
    gym_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("gyms.id", ondelete="SET NULL"),
        nullable=True,
    )
    session_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Ressenti 1-5
    feeling: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Intégration Strava
    strava_activity_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relations
    exercise_sets: Mapped[list["ExerciseSet"]] = relationship(
        "ExerciseSet", back_populates="performance_session", cascade="all, delete-orphan"
    )

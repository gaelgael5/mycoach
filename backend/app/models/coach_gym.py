"""Modèle CoachGym — B1-06 (M-M : coach_profiles ↔ gyms)."""

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CoachGym(Base):
    """Association many-to-many entre un coach et ses salles."""

    __tablename__ = "coach_gyms"
    __table_args__ = (
        UniqueConstraint("coach_id", "gym_id", name="uq_coach_gyms"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    gym_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("gyms.id", ondelete="CASCADE"),
        nullable=False,
    )

    coach: Mapped["CoachProfile"] = relationship("CoachProfile", back_populates="coach_gyms")  # type: ignore[name-defined]
    gym: Mapped["Gym"] = relationship("Gym", back_populates="coach_gyms")  # type: ignore[name-defined]

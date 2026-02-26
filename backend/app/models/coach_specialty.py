"""Modèle CoachSpecialty — B1-04."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Spécialités valides
SPECIALTY_VALUES = [
    "muscu", "cardio", "yoga", "pilates", "crossfit",
    "natation", "boxe", "running", "nutrition",
    "bien_etre", "rehabilitation", "sport_co", "autre",
]


class CoachSpecialty(Base):
    __tablename__ = "coach_specialties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    specialty: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="Valeurs : " + ", ".join(SPECIALTY_VALUES)
    )

    coach: Mapped["CoachProfile"] = relationship("CoachProfile", back_populates="specialties")  # type: ignore[name-defined]

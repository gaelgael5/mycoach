"""Modèle CoachAvailability — B1-08b."""

import uuid

from sqlalchemy import Boolean, ForeignKey, SmallInteger, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CoachAvailability(Base):
    """Créneaux de disponibilité dérivés du work_schedule.

    Chaque ligne représente un créneau horaire récurrent par jour de la semaine.
    max_slots = nombre de places simultanées par créneau.
    """

    __tablename__ = "coach_availability"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="0=Lundi … 6=Dimanche"
    )
    start_time: Mapped[object] = mapped_column(Time, nullable=False)
    end_time: Mapped[object] = mapped_column(Time, nullable=False)
    max_slots: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1,
        comment="Nombre de clients simultanés autorisés sur ce créneau"
    )
    booking_horizon_days: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=30,
        comment="Combien de jours à l'avance ce créneau est réservable"
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    coach: Mapped["CoachProfile"] = relationship("CoachProfile", back_populates="availability")  # type: ignore[name-defined]

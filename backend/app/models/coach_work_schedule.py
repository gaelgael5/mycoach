"""Modèle CoachWorkSchedule — B1-08."""

import uuid

from sqlalchemy import Boolean, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CoachWorkSchedule(Base):
    """Emploi du temps hebdomadaire du coach (créneaux disponibles par jour).

    time_slots : liste de créneaux JSON, ex :
        [{"start_time": "09:00", "end_time": "12:00"},
         {"start_time": "14:00", "end_time": "18:00"}]
    """

    __tablename__ = "coach_work_schedule"
    __table_args__ = (
        UniqueConstraint("coach_id", "day_of_week", name="uq_work_schedule_coach_day"),
    )

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
    is_working_day: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    time_slots: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list,
        comment='[{"start_time":"09:00","end_time":"12:00"}]'
    )

    coach: Mapped["CoachProfile"] = relationship("CoachProfile", back_populates="work_schedule")  # type: ignore[name-defined]

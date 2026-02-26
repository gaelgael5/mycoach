"""Modèle CancellationPolicy — B1-09."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CancellationPolicy(Base):
    """Politique d'annulation du coach (relation 1-1 avec coach_profiles).

    mode:
    - auto   → annulation tardive automatiquement facturée
    - manual → le coach décide manuellement si elle est facturée
    """

    __tablename__ = "cancellation_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="1-1 avec coach_profiles"
    )
    threshold_hours: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=24,
        comment="Délai en heures avant la séance en deçà duquel l'annulation est tardive"
    )
    mode: Mapped[str] = mapped_column(
        String(10), nullable=False, default="auto",
        comment="auto | manual"
    )
    noshow_is_due: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="True → no-show client = séance due (décomptée du forfait)"
    )
    client_message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Message affiché au client lors d'une annulation tardive"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    coach: Mapped["CoachProfile"] = relationship("CoachProfile", back_populates="cancellation_policy")  # type: ignore[name-defined]

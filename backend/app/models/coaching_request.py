"""Modèle CoachingRequest — B2-03."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

REQUEST_STATUSES = ["pending", "accepted", "rejected", "cancelled"]


class CoachingRequest(Base):
    """Demande de coaching envoyée par un client à un coach.

    Inclut optionnellement un slot de séance découverte.
    """

    __tablename__ = "coaching_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending",
        comment="pending | accepted | rejected | cancelled"
    )
    client_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Message d'introduction du client"
    )
    coach_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Réponse / raison de rejet du coach"
    )
    discovery_slot: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Créneau proposé pour la séance découverte (UTC)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]
    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_id])  # type: ignore[name-defined]

"""Modèle WaitlistEntry — B2-05."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

WAITLIST_STATUSES = ["waiting", "notified", "confirmed", "expired", "cancelled"]


class WaitlistEntry(Base):
    """Entrée dans la liste d'attente d'un créneau.

    Quand une place se libère, le 1er en statut 'waiting' passe à 'notified'
    et a 30 minutes pour confirmer (expires_at = now + 30min).
    """

    __tablename__ = "waitlist_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True,
        comment="Booking annulé qui a déclenché la notification (peut être NULL si créneau libre)"
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    slot_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        comment="Datetime du créneau convoité (UTC)"
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Position dans la file (1 = premier)"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="waiting",
        comment="waiting | notified | confirmed | expired | cancelled"
    )
    notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Date d'envoi de la notification push"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Fenêtre de confirmation : now() + 30min"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    booking: Mapped["Booking | None"] = relationship("Booking", back_populates="waitlist_entries")  # type: ignore[name-defined]
    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_id])  # type: ignore[name-defined]
    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]

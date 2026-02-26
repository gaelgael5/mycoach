"""Modèle Booking (séance réservée) — B2-04.

Machine d'état :
  pending_coach_validation → confirmed → done
                           → rejected
                           → auto_rejected (24h sans réponse coach)
  confirmed → cancelled_by_client (avant threshold_hours)
            → cancelled_late_by_client (après threshold_hours → séance due)
            → cancelled_by_coach (avant threshold_hours → notif client)
            → cancelled_by_coach_late (après threshold_hours → politique annulation)
            → no_show_client (coach marque no-show après séance)
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

BOOKING_STATUSES = [
    "pending_coach_validation",
    "confirmed",
    "done",
    "cancelled_by_client",
    "cancelled_late_by_client",   # pénalité : séance décomptée
    "cancelled_by_coach",
    "cancelled_by_coach_late",    # remboursement / geste commercial
    "rejected",
    "auto_rejected",
    "no_show_client",             # client absent → séance décomptée
]


class Booking(Base):
    """Réservation d'une séance de coaching."""

    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    pricing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coach_pricing.id", ondelete="SET NULL"), nullable=True
    )
    package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("packages.id", ondelete="SET NULL"), nullable=True
    )
    gym_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gyms.id", ondelete="SET NULL"), nullable=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        comment="Début de la séance (UTC)"
    )
    duration_min: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=60,
        comment="Durée en minutes"
    )
    status: Mapped[str] = mapped_column(
        String(40), nullable=False, default="pending_coach_validation",
        comment="Machine d'état — voir BOOKING_STATUSES"
    )
    # Prix effectif de cette séance (calculé à la confirmation)
    price_cents: Mapped[int | None] = mapped_column(
        Integer, nullable=True,
        comment="Prix de cette séance en centimes (nul si forfait)"
    )
    # Messages
    client_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Note du client lors de la réservation"
    )
    coach_cancel_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Raison d'annulation coach (libre)"
    )
    # Gestion pénalité
    late_cancel_waived: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="True si le coach a exonéré la pénalité d'annulation tardive"
    )
    # Métadonnées
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    done_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]
    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_id])  # type: ignore[name-defined]
    pricing: Mapped["CoachPricing | None"] = relationship("CoachPricing")  # type: ignore[name-defined]
    package: Mapped["Package | None"] = relationship("Package")  # type: ignore[name-defined]
    gym: Mapped["Gym | None"] = relationship("Gym")  # type: ignore[name-defined]
    waitlist_entries: Mapped[list["WaitlistEntry"]] = relationship(  # type: ignore[name-defined]
        "WaitlistEntry", back_populates="booking", cascade="all, delete-orphan"
    )

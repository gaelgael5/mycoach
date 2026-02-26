"""Modèle Package (forfait acheté) — B1-13."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

PACKAGE_STATUSES = ["active", "exhausted", "expired", "cancelled"]


class Package(Base):
    """Forfait de séances acheté par un client auprès d'un coach."""

    __tablename__ = "packages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    pricing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_pricing.id", ondelete="SET NULL"),
        nullable=True,
        comment="NULL si forfait personnalisé hors catalogue"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False,
        comment="Ex : 'Forfait 10 séances musculation'"
    )
    sessions_total: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="Nombre total de séances incluses"
    )
    sessions_remaining: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="Séances restantes — décrémenté après chaque séance done"
    )
    price_cents: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Prix total en centimes"
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="EUR",
        comment="ISO 4217"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active",
        comment="active | exhausted | expired | cancelled"
    )
    valid_until: Mapped[object | None] = mapped_column(
        Date, nullable=True,
        comment="Date d'expiration (optionnelle)"
    )
    alert_sent: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="True quand l'alerte '2 séances restantes' a été envoyée"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]
    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_id])  # type: ignore[name-defined]
    pricing: Mapped["CoachPricing | None"] = relationship("CoachPricing", back_populates="packages")  # type: ignore[name-defined]
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="package")  # type: ignore[name-defined]

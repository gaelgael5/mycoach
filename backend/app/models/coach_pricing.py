"""Modèle CoachPricing — B1-07."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Types de tarification
PRICING_TYPES = ["per_session", "package"]


class CoachPricing(Base):
    """Tarif coach : à la séance ou forfait N séances."""

    __tablename__ = "coach_pricing"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("coach_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="per_session | package"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    session_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1,
        comment="Toujours ≥ 1 ; = 1 pour per_session"
    )
    price_cents: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Montant en centimes (jamais float)"
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="EUR",
        comment="ISO 4217"
    )
    validity_months: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True,
        comment="Durée de validité en mois (pour forfaits)"
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="Visible par les clients potentiels"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    coach: Mapped["CoachProfile"] = relationship("CoachProfile", back_populates="pricing")  # type: ignore[name-defined]
    packages: Mapped[list["Package"]] = relationship("Package", back_populates="pricing")  # type: ignore[name-defined]

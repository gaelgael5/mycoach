"""Modèle Payment — B1-14."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

PAYMENT_METHODS = ["cash", "bank_transfer", "card", "check", "other"]
PAYMENT_STATUSES = ["pending", "paid", "late"]


class Payment(Base):
    """Enregistrement de paiement (manuel — pas de PSP intégré en Phase 1).

    Un paiement peut être lié à un forfait (package_id non nul) ou être
    un paiement à la séance (package_id nul).
    """

    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("packages.id", ondelete="RESTRICT"),
        nullable=True,
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount_cents: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Montant en centimes (jamais float)"
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="EUR",
        comment="ISO 4217"
    )
    payment_method: Mapped[str] = mapped_column(
        String(30), nullable=False, default="cash",
        comment="cash | bank_transfer | card | check | other"
    )
    reference: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Numéro de virement, référence chèque, etc."
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending",
        comment="pending | paid | late"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Date d'échéance si paiement différé"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    package: Mapped["Package | None"] = relationship("Package", back_populates="payments")  # type: ignore[name-defined]
    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_id])  # type: ignore[name-defined]
    client: Mapped["User"] = relationship("User", foreign_keys=[client_id])  # type: ignore[name-defined]

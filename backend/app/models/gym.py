"""Modèle Gym — B1-02."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Gym(Base):
    """Salle de sport individuelle."""

    __tablename__ = "gyms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    chain_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("gym_chains.id", ondelete="SET NULL"), nullable=True
    )
    external_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Identifiant dans la source externe (scraping)"
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(
        String(2), nullable=False, comment="ISO 3166-1 alpha-2"
    )
    latitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7), nullable=True
    )
    longitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7), nullable=True
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="E.164"
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    open_24h: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    validated: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Validé par un admin avant apparition dans l'app"
    )

    # Relations
    chain: Mapped["GymChain | None"] = relationship("GymChain", back_populates="gyms")  # type: ignore[name-defined]
    coach_gyms: Mapped[list["CoachGym"]] = relationship("CoachGym", back_populates="gym")  # type: ignore[name-defined]

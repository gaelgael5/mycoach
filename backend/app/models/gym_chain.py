"""Modèle GymChain — B1-01."""

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GymChain(Base):
    """Chaîne de salles de sport (Basic-Fit, Keep Cool, etc.)."""

    __tablename__ = "gym_chains"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(
        String(2), nullable=True, comment="ISO 3166-1 alpha-2 ; NULL = internationale"
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relations
    gyms: Mapped[list["Gym"]] = relationship("Gym", back_populates="chain")  # type: ignore[name-defined]

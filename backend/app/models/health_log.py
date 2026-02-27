"""Modèle HealthLog — historique des mesures de santé."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HealthLog(Base):
    __tablename__ = "health_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parameter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("health_parameters.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 'manual' | 'withings' | 'strava' | 'import'
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="health_logs")
    parameter: Mapped["HealthParameter"] = relationship("HealthParameter")

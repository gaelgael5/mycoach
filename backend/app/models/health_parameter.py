"""Modèle HealthParameter — liste des paramètres de santé administrables."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HealthParameter(Base):
    __tablename__ = "health_parameters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    # ex: {"fr": "Poids", "en": "Weight"}
    label: Mapped[dict] = mapped_column(JSONB, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "kg", "%", "bpm"
    # 'float' | 'int'
    data_type: Mapped[str] = mapped_column(String(10), nullable=False, default="float")
    # 'morphology' | 'cardiovascular' | 'sleep' | 'fitness' | 'nutrition' | 'other'
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="other")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

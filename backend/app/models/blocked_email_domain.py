"""Modèle BlockedEmailDomain — domaines email interdits à l'inscription."""
import uuid
from datetime import datetime
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class BlockedEmailDomain(Base):
    __tablename__ = "blocked_email_domains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    # domaine en minuscules, ex: "yopmail.com"
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # ex: "Service email jetable"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

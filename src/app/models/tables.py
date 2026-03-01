"""SQLAlchemy ORM models for MyCoach."""
import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    String, Text, Float, Integer, Boolean, Date, DateTime,
    ForeignKey, Enum as SAEnum, func, UniqueConstraint, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


def gen_uuid() -> uuid.UUID:
    return uuid.uuid4()


class Coach(Base):
    __tablename__ = "coaches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    plan: Mapped[str] = mapped_column(String(20), default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clients: Mapped[List["Client"]] = relationship(back_populates="coach", cascade="all, delete-orphan")
    programs: Mapped[List["Program"]] = relationship(back_populates="coach", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    coach_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("coaches.id"), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hourly_rate: Mapped[float] = mapped_column(Float, default=0.0)
    invitation_token: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    invitation_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    registered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("coach_id", "email", name="uq_client_coach_email"),
    )

    coach: Mapped["Coach"] = relationship(back_populates="clients")
    metrics: Mapped[List["Metric"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    session_logs: Mapped[List["SessionLog"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    program_assignments: Mapped[List["ProgramAssignment"]] = relationship(back_populates="client", cascade="all, delete-orphan")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    coach_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("coaches.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_weeks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    coach: Mapped["Coach"] = relationship(back_populates="programs")
    sessions: Mapped[List["ProgramSession"]] = relationship(back_populates="program", cascade="all, delete-orphan")
    assignments: Mapped[List["ProgramAssignment"]] = relationship(back_populates="program", cascade="all, delete-orphan")


class ProgramAssignment(Base):
    __tablename__ = "program_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False, index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("program_id", "client_id", name="uq_program_client"),
    )

    program: Mapped["Program"] = relationship(back_populates="assignments")
    client: Mapped["Client"] = relationship(back_populates="program_assignments")


class ProgramSession(Base):
    __tablename__ = "program_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False, index=True)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    program: Mapped["Program"] = relationship(back_populates="sessions")
    exercises: Mapped[List["Exercise"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    logs: Mapped[List["SessionLog"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("program_sessions.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sets: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reps: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rest_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["ProgramSession"] = relationship(back_populates="exercises")


class SessionLog(Base):
    __tablename__ = "session_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("program_sessions.id"), nullable=False, index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    actual_weights: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["ProgramSession"] = relationship(back_populates="logs")
    client: Mapped["Client"] = relationship(back_populates="session_logs")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    coach_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("coaches.id"), nullable=False, index=True)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    messages: Mapped[List["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    sender_type: Mapped[str] = mapped_column(String(10), nullable=False)
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    client: Mapped["Client"] = relationship(back_populates="metrics")

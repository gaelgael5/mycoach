"""Pydantic models for MyCoach."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


# ── Client ──────────────────────────────────────────────────

class ClientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    hourly_rate: Optional[float] = None  # € per hour


class ClientUpdate(ClientCreate):
    pass


class Client(ClientCreate):
    id: int
    created_at: datetime
    total_hours: float = 0.0
    total_paid: float = 0.0
    balance: float = 0.0  # amount due (positive = client owes money)


# ── Session (coaching hour) ──────────────────────────────────

class SessionCreate(BaseModel):
    client_id: int
    date: date
    duration_minutes: int          # e.g. 60 for 1h
    notes: Optional[str] = None
    billed: bool = True


class Session(SessionCreate):
    id: int
    created_at: datetime
    amount: float = 0.0            # computed from client hourly_rate


# ── Payment ──────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    client_id: int
    date: date
    amount: float
    method: Optional[str] = None   # cash, transfer, card...
    notes: Optional[str] = None


class Payment(PaymentCreate):
    id: int
    created_at: datetime


# ── Dashboard ────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_clients: int
    total_sessions: int
    total_hours: float
    total_revenue: float           # billed
    total_paid: float
    total_outstanding: float       # revenue - paid

"""Schemas Pydantic — Forfaits & Paiements (B1-19)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.models.payment import PAYMENT_METHODS, PAYMENT_STATUSES
from app.models.package import PACKAGE_STATUSES


# ── Forfaits (Packages) ───────────────────────────────────────────────────────

class PackageCreate(BaseModel):
    """Création d'un forfait pour un client."""
    pricing_id: uuid.UUID | None = None
    name: Annotated[str, Field(min_length=2, max_length=100)]
    sessions_total: Annotated[int, Field(ge=1, le=200)]
    price_cents: Annotated[int, Field(ge=0)]
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "EUR"
    valid_until: date | None = None


class PackageResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    coach_id: uuid.UUID
    pricing_id: uuid.UUID | None
    name: str
    sessions_total: int
    sessions_remaining: int
    price_cents: int
    currency: str
    status: str
    valid_until: date | None
    alert_sent: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Paiements ──────────────────────────────────────────────────────────────────

class PaymentRecord(BaseModel):
    """Enregistrement manuel d'un paiement par le coach."""
    package_id: uuid.UUID | None = None
    amount_cents: Annotated[int, Field(ge=0)]
    currency: Annotated[str, Field(min_length=3, max_length=3)] = "EUR"
    payment_method: str = "cash"
    reference: Annotated[str | None, Field(max_length=100)] = None
    description: Annotated[str | None, Field(max_length=500)] = None
    paid_at: datetime | None = None
    due_at: datetime | None = None

    @field_validator("payment_method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        if v not in PAYMENT_METHODS:
            raise ValueError(f"Méthode invalide. Valeurs : {PAYMENT_METHODS}")
        return v


class PaymentResponse(BaseModel):
    id: uuid.UUID
    package_id: uuid.UUID | None
    coach_id: uuid.UUID
    client_id: uuid.UUID
    amount_cents: int
    currency: str
    payment_method: str
    reference: str | None
    status: str
    description: str | None
    paid_at: datetime | None
    due_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentHistoryItem(BaseModel):
    """Item dans l'historique de paiement d'un client."""
    payment: PaymentResponse
    package_name: str | None  # résolu depuis package.name si disponible


class HoursSummary(BaseModel):
    """Résumé des heures/séances pour un client."""
    client_id: uuid.UUID
    active_package: PackageResponse | None
    sessions_total_all_time: int
    sessions_remaining: int  # dans le forfait actif, 0 si aucun
    sessions_done: int       # séances effectuées (tous forfaits)
    sessions_due: int        # séances dues non payées
    alert_low_sessions: bool  # True si sessions_remaining <= 2

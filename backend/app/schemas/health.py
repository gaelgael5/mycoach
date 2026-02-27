"""Schémas Pydantic — Paramètres de santé, logs, partage."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

VALID_SOURCES = ["manual", "withings", "strava", "import"]
VALID_DATA_TYPES = ["float", "int"]
VALID_CATEGORIES = ["morphology", "cardiovascular", "sleep", "fitness", "nutrition", "other"]


# ---------------------------------------------------------------------------
# Paramètres de santé (admin-configurable)
# ---------------------------------------------------------------------------

class HealthParameterCreate(BaseModel):
    slug: str
    label: dict
    unit: Optional[str] = None
    data_type: str = "float"
    category: str = "other"
    position: int = 0

    @field_validator("data_type")
    @classmethod
    def data_type_valid(cls, v: str) -> str:
        if v not in VALID_DATA_TYPES:
            raise ValueError(f"data_type must be one of {VALID_DATA_TYPES}")
        return v

    @field_validator("category")
    @classmethod
    def category_valid(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        return v


class HealthParameterUpdate(BaseModel):
    label: Optional[dict] = None
    unit: Optional[str] = None
    data_type: Optional[str] = None
    category: Optional[str] = None
    active: Optional[bool] = None
    position: Optional[int] = None

    @field_validator("data_type")
    @classmethod
    def data_type_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_DATA_TYPES:
            raise ValueError(f"data_type must be one of {VALID_DATA_TYPES}")
        return v

    @field_validator("category")
    @classmethod
    def category_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        return v


class HealthParameterResponse(BaseModel):
    id: uuid.UUID
    slug: str
    label: dict
    unit: Optional[str]
    data_type: str
    category: str
    active: bool
    position: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Logs de mesures
# ---------------------------------------------------------------------------

class HealthLogCreate(BaseModel):
    parameter_id: uuid.UUID
    value: float
    note: Optional[str] = None
    source: str = "manual"
    logged_at: datetime

    @field_validator("source")
    @classmethod
    def source_valid(cls, v: str) -> str:
        if v not in VALID_SOURCES:
            raise ValueError(f"source must be one of {VALID_SOURCES}")
        return v


class HealthLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    parameter: HealthParameterResponse
    value: float
    note: Optional[str]
    source: str
    logged_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Préférences de partage
# ---------------------------------------------------------------------------

class HealthSharingItem(BaseModel):
    parameter_id: uuid.UUID
    shared: bool


class HealthSharingUpdate(BaseModel):
    updates: list[HealthSharingItem]


class HealthSharingResponse(BaseModel):
    parameter_id: uuid.UUID
    shared: bool

    model_config = {"from_attributes": True}

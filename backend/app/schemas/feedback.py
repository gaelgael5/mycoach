"""Schémas Pydantic — Feedback utilisateur (suggestions & bugs)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

VALID_TYPES = ["suggestion", "bug_report"]
VALID_STATUSES = ["pending", "reviewing", "resolved", "rejected"]
VALID_PLATFORMS = ["android", "ios", "web"]


class FeedbackCreate(BaseModel):
    type: str
    title: str
    description: str
    app_version: Optional[str] = None
    platform: Optional[str] = None

    @field_validator("type")
    @classmethod
    def type_valid(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(f"type must be one of {VALID_TYPES}")
        return v

    @field_validator("title")
    @classmethod
    def title_max(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be empty")
        if len(v) > 200:
            raise ValueError("title must be at most 200 characters")
        return v

    @field_validator("description")
    @classmethod
    def desc_max(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("description cannot be empty")
        if len(v) > 5000:
            raise ValueError("description must be at most 5000 characters")
        return v

    @field_validator("platform")
    @classmethod
    def platform_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PLATFORMS:
            raise ValueError(f"platform must be one of {VALID_PLATFORMS}")
        return v


class FeedbackAdminUpdate(BaseModel):
    status: Optional[str] = None
    admin_note: Optional[str] = None

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    type: str
    title: str
    description: str
    app_version: Optional[str]
    platform: Optional[str]
    status: str
    admin_note: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

"""Schemas Pydantic — Templates de messages d'annulation (B1-31)."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.cancellation_message_template import TEMPLATE_VARIABLES

# Pattern pour détecter les variables dans le body
_VAR_PATTERN = re.compile(r"\{[^}]+\}")
_VALID_VARS = set(TEMPLATE_VARIABLES)


def _extract_variables(body: str) -> list[str]:
    """Extrait les variables reconnues dans le body du template."""
    found = _VAR_PATTERN.findall(body)
    return [v for v in found if v in _VALID_VARS]


class CancellationTemplateCreate(BaseModel):
    title: Annotated[str, Field(min_length=2, max_length=40)]
    body: Annotated[str, Field(min_length=10, max_length=300)]

    @field_validator("body")
    @classmethod
    def validate_no_unknown_vars(cls, v: str) -> str:
        found = _VAR_PATTERN.findall(v)
        unknown = [x for x in found if x not in _VALID_VARS]
        if unknown:
            raise ValueError(
                f"Variables inconnues : {unknown}. "
                f"Variables autorisées : {TEMPLATE_VARIABLES}"
            )
        return v


class CancellationTemplateUpdate(BaseModel):
    title: Annotated[str | None, Field(min_length=2, max_length=40)] = None
    body: Annotated[str | None, Field(min_length=10, max_length=300)] = None
    position: Annotated[int | None, Field(ge=1, le=5)] = None

    @field_validator("body")
    @classmethod
    def validate_no_unknown_vars(cls, v: str | None) -> str | None:
        if v is None:
            return v
        found = _VAR_PATTERN.findall(v)
        unknown = [x for x in found if x not in _VALID_VARS]
        if unknown:
            raise ValueError(
                f"Variables inconnues : {unknown}. "
                f"Variables autorisées : {TEMPLATE_VARIABLES}"
            )
        return v


class CancellationTemplateResponse(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    is_default: bool
    position: int
    variables_used: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CancellationTemplatePreviewRequest(BaseModel):
    """Prévisualisation d'un template résolu avec des données de séance."""
    client_first_name: str
    session_date: str   # "26/02/2026"
    session_time: str   # "10:00"
    coach_name: str


class CancellationTemplatePreview(BaseModel):
    """Template avec variables résolues."""
    template_id: uuid.UUID
    resolved_body: str
    client_name: str


class CancellationTemplateReorderItem(BaseModel):
    id: uuid.UUID
    position: Annotated[int, Field(ge=1, le=5)]


class CancellationTemplateReorderRequest(BaseModel):
    items: list[CancellationTemplateReorderItem]

    @model_validator(mode="after")
    def validate_unique_positions(self) -> "CancellationTemplateReorderRequest":
        positions = [i.position for i in self.items]
        if len(positions) != len(set(positions)):
            raise ValueError("Les positions doivent être uniques")
        return self

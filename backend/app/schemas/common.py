"""Schemas Pydantic communs — réponses génériques."""
from typing import Generic, TypeVar
from pydantic import BaseModel


def resolve_avatar_url(avatar_url: str | None, gender: str | None) -> str:
    """Retourne l'URL de l'avatar ou un avatar par défaut selon le genre."""
    if avatar_url:
        return avatar_url
    defaults = {
        "male": "/static/avatars/default_male.svg",
        "female": "/static/avatars/default_female.svg",
    }
    return defaults.get(gender or "", "/static/avatars/default_neutral.svg")

T = TypeVar("T")


class ErrorResponse(BaseModel):
    detail: str  # Message i18n — jamais de string codée en dur


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int
    has_more: bool

    @classmethod
    def from_results(
        cls,
        items: list[T],
        total: int,
        offset: int,
        limit: int,
    ) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total,
        )

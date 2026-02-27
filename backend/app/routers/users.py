"""Router — Profil utilisateur (genre, année de naissance)."""
from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

VALID_GENDERS = {"male", "female", "other"}
CURRENT_YEAR = dt.datetime.now().year


class UserProfileUpdate(BaseModel):
    gender: Optional[str] = None   # 'male' | 'female' | 'other'
    birth_year: Optional[int] = None  # entre 1900 et année courante

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_GENDERS:
            raise ValueError(f"Genre invalide. Valeurs : {sorted(VALID_GENDERS)}")
        return v

    @field_validator("birth_year")
    @classmethod
    def validate_birth_year(cls, v: int | None) -> int | None:
        if v is not None:
            current_year = dt.datetime.now().year
            if v < 1900 or v > current_year:
                raise ValueError(f"Année de naissance invalide (1900–{current_year})")
        return v


@router.patch("/me/profile", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    body: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mise à jour du genre et de l'année de naissance de l'utilisateur connecté."""
    if body.gender is not None:
        current_user.gender = body.gender
    if body.birth_year is not None:
        current_user.birth_year = body.birth_year
    await db.flush()
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.from_user(current_user)

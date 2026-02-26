"""Router push tokens — B2-23."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/push", tags=["push"])


class PushTokenRegister(BaseModel):
    token: str
    platform: str  # android | ios


@router.post("/register", response_model=MessageResponse)
async def register_token(
    data: PushTokenRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.platform not in ("android", "ios"):
        raise HTTPException(status_code=422, detail="platform doit être 'android' ou 'ios'")
    from app.repositories.push_token_repository import upsert_token
    await upsert_token(db, current_user.id, data.token, data.platform)
    await db.commit()
    return {"message": "Token enregistré"}

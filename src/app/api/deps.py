"""Shared FastAPI dependencies."""
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.tables import Coach
from app.services.auth import decode_token

bearer_scheme = HTTPBearer()


async def get_current_coach(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Coach:
    """Extract and validate the current coach from the JWT access token."""
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    coach_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(Coach).where(Coach.id == coach_id))
    coach = result.scalar_one_or_none()
    if coach is None or not coach.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Coach not found or inactive")
    return coach

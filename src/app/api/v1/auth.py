"""Auth router: register, login, refresh."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.tables import Coach
from app.schemas.auth import CoachRegister, LoginRequest, TokenResponse, RefreshRequest
from app.services.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: CoachRegister, db: AsyncSession = Depends(get_db)):
    """Register a new coach account."""
    exists = await db.execute(select(func.count()).where(Coach.email == body.email))
    if exists.scalar_one() > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    coach = Coach(
        email=body.email,
        hashed_password=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
    )
    db.add(coach)
    await db.flush()

    return TokenResponse(
        access_token=create_access_token(coach.id),
        refresh_token=create_refresh_token(coach.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and return JWT tokens."""
    result = await db.execute(select(Coach).where(Coach.email == body.email))
    coach = result.scalar_one_or_none()
    if coach is None or not verify_password(body.password, coach.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(coach.id),
        refresh_token=create_refresh_token(coach.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Get new tokens from a valid refresh token."""
    payload = decode_token(body.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    import uuid
    coach_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(Coach).where(Coach.id == coach_id))
    coach = result.scalar_one_or_none()
    if coach is None or not coach.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Coach not found")

    return TokenResponse(
        access_token=create_access_token(coach.id),
        refresh_token=create_refresh_token(coach.id),
    )

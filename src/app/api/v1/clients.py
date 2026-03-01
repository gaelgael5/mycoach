"""Clients router with freemium guard."""
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.base import get_db
from app.models.tables import Coach, Client
from app.api.deps import get_current_coach
from app.schemas.client import (
    ClientCreate, ClientUpdate, ClientRead,
    ClientInvite, ClientInviteResponse, ClientRegisterViaToken,
)
from app.services.auth import hash_password
from app.api.v1.conversations import ensure_conversation

router = APIRouter(prefix="/clients", tags=["clients"])
settings = get_settings()


async def _check_freemium(db: AsyncSession, coach: Coach):
    """Raise 403 if coach is on free plan and already at max clients."""
    if coach.plan != "free":
        return
    count = await db.execute(
        select(func.count()).where(Client.coach_id == coach.id, Client.is_active == True)
    )
    if count.scalar_one() >= settings.FREE_PLAN_MAX_CLIENTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Free plan limited to {settings.FREE_PLAN_MAX_CLIENTS} clients. Upgrade to add more.",
        )


@router.get("", response_model=list[ClientRead])
async def list_clients(
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """List all clients for the authenticated coach."""
    result = await db.execute(
        select(Client).where(Client.coach_id == coach.id).order_by(Client.last_name)
    )
    return result.scalars().all()


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    body: ClientCreate,
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Create a new client (freemium guard applied)."""
    await _check_freemium(db, coach)
    client = Client(coach_id=coach.id, **body.model_dump())
    db.add(client)
    await db.flush()
    await db.refresh(client)
    # Auto-create conversation for this client
    await ensure_conversation(db, coach.id, client.id)
    return client


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Get a single client by ID."""
    import uuid
    result = await db.execute(
        select(Client).where(Client.id == uuid.UUID(client_id), Client.coach_id == coach.id)
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: str,
    body: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Update client fields."""
    import uuid
    result = await db.execute(
        select(Client).where(Client.id == uuid.UUID(client_id), Client.coach_id == coach.id)
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    await db.flush()
    await db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Soft-delete a client."""
    import uuid
    result = await db.execute(
        select(Client).where(Client.id == uuid.UUID(client_id), Client.coach_id == coach.id)
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    client.is_active = False
    await db.flush()


@router.post("/invite", response_model=ClientInviteResponse)
async def invite_client(
    body: ClientInvite,
    db: AsyncSession = Depends(get_db),
    coach: Coach = Depends(get_current_coach),
):
    """Generate an invitation token for a client to self-register."""
    result = await db.execute(
        select(Client).where(Client.id == body.client_id, Client.coach_id == coach.id)
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    token = secrets.token_urlsafe(32)
    client.invitation_token = token
    client.invitation_sent_at = datetime.now(timezone.utc)
    await db.flush()

    return ClientInviteResponse(
        invitation_token=token,
        invitation_url=f"{settings.BASE_URL}/api/v1/clients/register?token={token}",
    )


@router.post("/register", response_model=ClientRead)
async def register_via_token(
    body: ClientRegisterViaToken,
    db: AsyncSession = Depends(get_db),
):
    """Client self-registration via invitation token (no auth required)."""
    result = await db.execute(
        select(Client).where(Client.invitation_token == body.token)
    )
    client = result.scalar_one_or_none()
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invitation token")
    if client.registered_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already registered")

    client.email = body.email
    client.hashed_password = hash_password(body.password)
    client.registered_at = datetime.now(timezone.utc)
    client.invitation_token = None  # Consume the token
    await db.flush()
    await db.refresh(client)
    return client

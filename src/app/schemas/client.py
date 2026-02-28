"""Client schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None
    hourly_rate: float = 0.0


class ClientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None
    hourly_rate: float | None = None


class ClientRead(BaseModel):
    id: uuid.UUID
    coach_id: uuid.UUID
    email: str | None = None
    first_name: str
    last_name: str
    phone: str | None = None
    notes: str | None = None
    hourly_rate: float
    is_active: bool
    registered_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientInvite(BaseModel):
    client_id: uuid.UUID


class ClientInviteResponse(BaseModel):
    invitation_token: str
    invitation_url: str


class ClientRegisterViaToken(BaseModel):
    token: str
    email: EmailStr
    password: str

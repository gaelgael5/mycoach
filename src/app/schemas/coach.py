"""Coach schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class CoachRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    plan: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CoachUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    bio: str | None = None
    avatar_url: str | None = None

"""Auth schemas (Pydantic v2)."""
import uuid
from pydantic import BaseModel, EmailStr


class CoachRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str  # coach UUID
    type: str  # "access" | "refresh"

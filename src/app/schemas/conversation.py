"""Schemas for conversations and messages."""
import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_type: str
    sender_id: uuid.UUID
    content: str
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationRead(BaseModel):
    id: uuid.UUID
    coach_id: uuid.UUID
    client_id: uuid.UUID
    created_at: datetime
    last_message: Optional[MessageRead] = None
    unread_count: int = 0

    model_config = {"from_attributes": True}


class PaginatedMessages(BaseModel):
    items: list[MessageRead]
    total_count: int
    limit: int
    offset: int

"""Schemas Pydantic pour SMS — B2-30."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class SmsLogResponse(BaseModel):
    id: UUID
    recipient_phone: str
    message_body: str
    status: str
    sent_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BulkCancelRequest(BaseModel):
    booking_ids: list[UUID]
    template_id: UUID | None = None
    custom_message: str | None = None
    send_sms: bool = True


class BulkCancelResponse(BaseModel):
    cancelled_count: int
    sms_sent_count: int
    sms_failed_count: int
    failed_clients: list[str]


class SmsBroadcastRequest(BaseModel):
    scope: Literal["all", "day", "manual"]
    day: date | None = None
    client_ids: list[UUID] | None = None
    template_id: UUID | None = None
    custom_message: str | None = None


class SmsBroadcastResponse(BaseModel):
    sent_count: int
    failed_count: int
    no_phone_count: int

"""Repository sms_logs."""
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sms_log import SmsLog


async def create_log(db, coach_id, recipient_phone, message_body, *, client_id=None, template_id=None) -> SmsLog:
    obj = SmsLog(
        id=uuid.uuid4(),
        coach_id=coach_id,
        client_id=client_id,
        template_id=template_id,
        recipient_phone=recipient_phone,
        message_body=message_body,
        status="pending",
    )
    db.add(obj)
    await db.flush()
    return obj


async def update_status(db, log: SmsLog, status: str, *, provider_message_id=None, error_message=None) -> SmsLog:
    log.status = status
    if provider_message_id:
        log.provider_message_id = provider_message_id
    if error_message:
        log.error_message = error_message
    if status == "sent":
        log.sent_at = datetime.now(timezone.utc)
    await db.flush()
    return log


async def list_by_coach(db, coach_id, *, status=None, offset=0, limit=50) -> tuple[list[SmsLog], int]:
    base = select(SmsLog).where(SmsLog.coach_id == coach_id)
    if status:
        base = base.where(SmsLog.status == status)
    count = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    items = list(
        (await db.execute(base.order_by(SmsLog.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    )
    return items, count


async def get_by_id(db, log_id: uuid.UUID) -> SmsLog | None:
    result = await db.execute(select(SmsLog).where(SmsLog.id == log_id))
    return result.scalar_one_or_none()

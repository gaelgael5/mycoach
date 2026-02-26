"""Repository push_tokens."""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.push_token import PushToken


async def upsert_token(db, user_id, token, platform) -> PushToken:
    q = select(PushToken).where(PushToken.user_id == user_id, PushToken.token == token)
    result = await db.execute(q)
    obj = result.scalar_one_or_none()
    if obj is None:
        obj = PushToken(id=uuid.uuid4(), user_id=user_id, token=token, platform=platform, active=True)
        db.add(obj)
    else:
        obj.active = True
        obj.platform = platform
    await db.flush()
    return obj


async def get_active_tokens(db, user_id) -> list[PushToken]:
    q = select(PushToken).where(PushToken.user_id == user_id, PushToken.active == True)
    result = await db.execute(q)
    return list(result.scalars().all())


async def deactivate_token(db, token_str: str) -> None:
    q = select(PushToken).where(PushToken.token == token_str)
    result = await db.execute(q)
    obj = result.scalar_one_or_none()
    if obj:
        obj.active = False
        await db.flush()

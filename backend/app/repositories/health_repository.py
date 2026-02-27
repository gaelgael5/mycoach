"""Repository — HealthParameter, HealthLog, HealthSharingSetting."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_log import HealthLog
from app.models.health_parameter import HealthParameter
from app.models.health_sharing_setting import HealthSharingSetting


# ---------------------------------------------------------------------------
# HealthParameter
# ---------------------------------------------------------------------------

async def get_parameters(
    db: AsyncSession,
    active_only: bool = True,
) -> list[HealthParameter]:
    q = select(HealthParameter).order_by(HealthParameter.position)
    if active_only:
        q = q.where(HealthParameter.active.is_(True))
    return list((await db.execute(q)).scalars().all())


async def get_parameter_by_id(
    db: AsyncSession,
    param_id: uuid.UUID,
) -> HealthParameter | None:
    q = select(HealthParameter).where(HealthParameter.id == param_id)
    return (await db.execute(q)).scalar_one_or_none()


async def get_parameter_by_slug(
    db: AsyncSession,
    slug: str,
) -> HealthParameter | None:
    q = select(HealthParameter).where(HealthParameter.slug == slug)
    return (await db.execute(q)).scalar_one_or_none()


async def create_parameter(
    db: AsyncSession,
    slug: str,
    label: dict,
    unit: Optional[str],
    data_type: str,
    category: str,
    position: int,
) -> HealthParameter:
    param = HealthParameter(
        slug=slug,
        label=label,
        unit=unit,
        data_type=data_type,
        category=category,
        position=position,
    )
    db.add(param)
    await db.flush()
    await db.refresh(param)
    return param


async def update_parameter(
    db: AsyncSession,
    param: HealthParameter,
    **fields,
) -> HealthParameter:
    for key, value in fields.items():
        if value is not None:
            setattr(param, key, value)
    await db.flush()
    await db.refresh(param)
    return param


async def soft_delete_parameter(
    db: AsyncSession,
    param: HealthParameter,
) -> HealthParameter:
    param.active = False
    await db.flush()
    await db.refresh(param)
    return param


# ---------------------------------------------------------------------------
# HealthLog
# ---------------------------------------------------------------------------

async def create_log(
    db: AsyncSession,
    user_id: uuid.UUID,
    parameter_id: uuid.UUID,
    value: float,
    note: Optional[str],
    source: str,
    logged_at: datetime,
) -> HealthLog:
    log = HealthLog(
        user_id=user_id,
        parameter_id=parameter_id,
        value=value,
        note=note,
        source=source,
        logged_at=logged_at,
    )
    db.add(log)
    await db.flush()
    # Reload with relationships eagerly via selectin
    q = select(HealthLog).where(HealthLog.id == log.id)
    from sqlalchemy.orm import selectinload
    q = q.options(selectinload(HealthLog.parameter))
    result = (await db.execute(q)).scalar_one()
    return result


async def get_logs(
    db: AsyncSession,
    user_id: uuid.UUID,
    parameter_id: Optional[uuid.UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> list[HealthLog]:
    from sqlalchemy.orm import selectinload
    q = (
        select(HealthLog)
        .where(HealthLog.user_id == user_id)
        .options(selectinload(HealthLog.parameter))
        .order_by(HealthLog.logged_at.desc())
    )
    if parameter_id:
        q = q.where(HealthLog.parameter_id == parameter_id)
    if from_date:
        q = q.where(HealthLog.logged_at >= from_date)
    if to_date:
        q = q.where(HealthLog.logged_at <= to_date)
    return list((await db.execute(q)).scalars().all())


async def get_log_by_id(
    db: AsyncSession,
    log_id: uuid.UUID,
    user_id: uuid.UUID,
) -> HealthLog | None:
    from sqlalchemy.orm import selectinload
    q = (
        select(HealthLog)
        .where(HealthLog.id == log_id, HealthLog.user_id == user_id)
        .options(selectinload(HealthLog.parameter))
    )
    return (await db.execute(q)).scalar_one_or_none()


async def delete_log(
    db: AsyncSession,
    log_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    log = await get_log_by_id(db, log_id, user_id)
    if log is None:
        return False
    await db.delete(log)
    await db.flush()
    return True


# ---------------------------------------------------------------------------
# HealthSharingSetting
# ---------------------------------------------------------------------------

async def get_sharing_settings(
    db: AsyncSession,
    user_id: uuid.UUID,
    coach_id: uuid.UUID,
) -> list[HealthSharingSetting]:
    q = select(HealthSharingSetting).where(
        HealthSharingSetting.user_id == user_id,
        HealthSharingSetting.coach_id == coach_id,
    )
    return list((await db.execute(q)).scalars().all())


async def get_sharing_setting(
    db: AsyncSession,
    user_id: uuid.UUID,
    coach_id: uuid.UUID,
    parameter_id: uuid.UUID,
) -> HealthSharingSetting | None:
    q = select(HealthSharingSetting).where(
        HealthSharingSetting.user_id == user_id,
        HealthSharingSetting.coach_id == coach_id,
        HealthSharingSetting.parameter_id == parameter_id,
    )
    return (await db.execute(q)).scalar_one_or_none()


async def upsert_sharing(
    db: AsyncSession,
    user_id: uuid.UUID,
    coach_id: uuid.UUID,
    parameter_id: uuid.UUID,
    shared: bool,
) -> HealthSharingSetting:
    existing = await get_sharing_setting(db, user_id, coach_id, parameter_id)
    if existing:
        existing.shared = shared
        await db.flush()
        await db.refresh(existing)
        return existing
    setting = HealthSharingSetting(
        user_id=user_id,
        coach_id=coach_id,
        parameter_id=parameter_id,
        shared=shared,
    )
    db.add(setting)
    await db.flush()
    await db.refresh(setting)
    return setting


async def is_parameter_shared(
    db: AsyncSession,
    user_id: uuid.UUID,
    coach_id: uuid.UUID,
    parameter_id: uuid.UUID,
) -> bool:
    """Returns True if no row (default=shared) or shared=True."""
    setting = await get_sharing_setting(db, user_id, coach_id, parameter_id)
    if setting is None:
        return True
    return setting.shared

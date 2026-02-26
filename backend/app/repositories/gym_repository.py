"""Repository gym — B1-21."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gym import Gym
from app.models.gym_chain import GymChain


async def search(
    db: AsyncSession,
    *,
    chain_id: uuid.UUID | None = None,
    country: str | None = None,
    city: str | None = None,
    zip_code: str | None = None,
    q: str | None = None,
    validated_only: bool = True,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Gym], int]:
    """Recherche de salles avec filtres. Retourne (items, total)."""
    base = select(Gym)
    if validated_only:
        base = base.where(Gym.validated.is_(True))
    if chain_id:
        base = base.where(Gym.chain_id == chain_id)
    if country:
        base = base.where(func.lower(Gym.country) == country.lower())
    if city:
        base = base.where(func.lower(Gym.city) == city.lower())
    if zip_code:
        base = base.where(Gym.zip_code == zip_code)
    if q:
        pattern = f"%{q.lower()}%"
        base = base.where(
            or_(
                func.lower(Gym.name).like(pattern),
                func.lower(Gym.city).like(pattern),
                func.lower(Gym.address).like(pattern),
            )
        )

    count_q = select(func.count()).select_from(base.subquery())
    count_result = await db.execute(count_q)
    total = count_result.scalar_one()

    items_q = base.order_by(Gym.city, Gym.name).offset(offset).limit(limit)
    items_result = await db.execute(items_q)
    return list(items_result.scalars().all()), total


async def get_by_id(db: AsyncSession, gym_id: uuid.UUID) -> Gym | None:
    q = select(Gym).where(Gym.id == gym_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def get_chains(
    db: AsyncSession,
    *,
    country: str | None = None,
    active_only: bool = True,
    offset: int = 0,
    limit: int = 100,
) -> list[GymChain]:
    q = select(GymChain)
    if active_only:
        q = q.where(GymChain.active.is_(True))
    if country:
        q = q.where(
            or_(
                func.lower(GymChain.country) == country.lower(),
                GymChain.country.is_(None),
            )
        )
    q = q.order_by(GymChain.name).offset(offset).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_chain_by_id(
    db: AsyncSession, chain_id: uuid.UUID
) -> GymChain | None:
    q = select(GymChain).where(GymChain.id == chain_id)
    result = await db.execute(q)
    return result.scalar_one_or_none()

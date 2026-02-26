"""Repository coach — B1-20."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.coach_profile import CoachProfile
from app.models.coach_specialty import CoachSpecialty
from app.models.coach_certification import CoachCertification
from app.models.coach_gym import CoachGym
from app.models.coach_pricing import CoachPricing
from app.models.coach_availability import CoachAvailability
from app.models.cancellation_policy import CancellationPolicy
from app.models.coaching_relation import CoachingRelation
from app.models.coach_client_note import CoachClientNote


def _with_relations() -> list:
    return [
        selectinload(CoachProfile.specialties),
        selectinload(CoachProfile.certifications),
        selectinload(CoachProfile.pricing),
        selectinload(CoachProfile.availability),
        selectinload(CoachProfile.cancellation_policy),
    ]


async def get_by_user_id(
    db: AsyncSession, user_id: uuid.UUID, *, load_relations: bool = True
) -> CoachProfile | None:
    opts = _with_relations() if load_relations else []
    q = select(CoachProfile).where(CoachProfile.user_id == user_id)
    for o in opts:
        q = q.options(o)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def get_by_id(
    db: AsyncSession, profile_id: uuid.UUID, *, load_relations: bool = True
) -> CoachProfile | None:
    opts = _with_relations() if load_relations else []
    q = select(CoachProfile).where(CoachProfile.id == profile_id)
    for o in opts:
        q = q.options(o)
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def create_profile(
    db: AsyncSession, user_id: uuid.UUID, **kwargs: Any
) -> CoachProfile:
    profile = CoachProfile(id=uuid.uuid4(), user_id=user_id, **kwargs)
    db.add(profile)
    await db.flush()
    return profile


async def update_profile(
    db: AsyncSession, profile: CoachProfile, **kwargs: Any
) -> CoachProfile:
    for key, val in kwargs.items():
        setattr(profile, key, val)
    await db.flush()
    return profile


# ── Spécialités ───────────────────────────────────────────────────────────────

async def add_specialty(
    db: AsyncSession, coach_id: uuid.UUID, specialty: str
) -> CoachSpecialty:
    obj = CoachSpecialty(id=uuid.uuid4(), coach_id=coach_id, specialty=specialty)
    db.add(obj)
    await db.flush()
    return obj


async def remove_specialty(
    db: AsyncSession, coach_id: uuid.UUID, specialty_id: uuid.UUID
) -> bool:
    q = select(CoachSpecialty).where(
        CoachSpecialty.id == specialty_id,
        CoachSpecialty.coach_id == coach_id,
    )
    result = await db.execute(q)
    obj = result.scalar_one_or_none()
    if obj is None:
        return False
    await db.delete(obj)
    await db.flush()
    return True


# ── Certifications ────────────────────────────────────────────────────────────

async def add_certification(
    db: AsyncSession, coach_id: uuid.UUID, **kwargs: Any
) -> CoachCertification:
    obj = CoachCertification(id=uuid.uuid4(), coach_id=coach_id, **kwargs)
    db.add(obj)
    await db.flush()
    return obj


async def remove_certification(
    db: AsyncSession, coach_id: uuid.UUID, cert_id: uuid.UUID
) -> bool:
    q = select(CoachCertification).where(
        CoachCertification.id == cert_id,
        CoachCertification.coach_id == coach_id,
    )
    result = await db.execute(q)
    obj = result.scalar_one_or_none()
    if obj is None:
        return False
    await db.delete(obj)
    await db.flush()
    return True


# ── Pricing ───────────────────────────────────────────────────────────────────

async def add_pricing(
    db: AsyncSession, coach_id: uuid.UUID, **kwargs: Any
) -> CoachPricing:
    obj = CoachPricing(id=uuid.uuid4(), coach_id=coach_id, **kwargs)
    db.add(obj)
    await db.flush()
    return obj


async def get_pricing(
    db: AsyncSession, coach_id: uuid.UUID, pricing_id: uuid.UUID
) -> CoachPricing | None:
    q = select(CoachPricing).where(
        CoachPricing.id == pricing_id,
        CoachPricing.coach_id == coach_id,
    )
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def update_pricing(
    db: AsyncSession, obj: CoachPricing, **kwargs: Any
) -> CoachPricing:
    for k, v in kwargs.items():
        setattr(obj, k, v)
    await db.flush()
    return obj


async def delete_pricing(db: AsyncSession, obj: CoachPricing) -> None:
    await db.delete(obj)
    await db.flush()


# ── Disponibilités ────────────────────────────────────────────────────────────

async def add_availability(
    db: AsyncSession, coach_id: uuid.UUID, **kwargs: Any
) -> CoachAvailability:
    from datetime import time as dt_time
    # asyncpg ne sait pas convertir "HH:MM" en time — on le fait ici
    for field in ("start_time", "end_time"):
        val = kwargs.get(field)
        if isinstance(val, str):
            h, m = val.split(":")
            kwargs[field] = dt_time(int(h), int(m))
    obj = CoachAvailability(id=uuid.uuid4(), coach_id=coach_id, **kwargs)
    db.add(obj)
    await db.flush()
    return obj


async def get_availability(
    db: AsyncSession, coach_id: uuid.UUID, avail_id: uuid.UUID
) -> CoachAvailability | None:
    q = select(CoachAvailability).where(
        CoachAvailability.id == avail_id,
        CoachAvailability.coach_id == coach_id,
    )
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def delete_availability(db: AsyncSession, obj: CoachAvailability) -> None:
    await db.delete(obj)
    await db.flush()


# ── Politique d'annulation ────────────────────────────────────────────────────

async def upsert_cancellation_policy(
    db: AsyncSession, coach_id: uuid.UUID, **kwargs: Any
) -> CancellationPolicy:
    q = select(CancellationPolicy).where(CancellationPolicy.coach_id == coach_id)
    result = await db.execute(q)
    policy = result.scalar_one_or_none()
    if policy is None:
        policy = CancellationPolicy(id=uuid.uuid4(), coach_id=coach_id, **kwargs)
        db.add(policy)
    else:
        for k, v in kwargs.items():
            setattr(policy, k, v)
    await db.flush()
    return policy


# ── Relations coach/client ────────────────────────────────────────────────────

async def get_clients(
    db: AsyncSession,
    coach_id: uuid.UUID,
    *,
    status: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> list[CoachingRelation]:
    q = select(CoachingRelation).where(CoachingRelation.coach_id == coach_id)
    if status:
        q = q.where(CoachingRelation.status == status)
    q = q.offset(offset).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_relation(
    db: AsyncSession, coach_id: uuid.UUID, client_id: uuid.UUID
) -> CoachingRelation | None:
    q = select(CoachingRelation).where(
        CoachingRelation.coach_id == coach_id,
        CoachingRelation.client_id == client_id,
    )
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def upsert_relation(
    db: AsyncSession, coach_id: uuid.UUID, client_id: uuid.UUID, status: str
) -> CoachingRelation:
    rel = await get_relation(db, coach_id, client_id)
    if rel is None:
        rel = CoachingRelation(
            id=uuid.uuid4(), coach_id=coach_id, client_id=client_id, status=status
        )
        db.add(rel)
    else:
        rel.status = status
    await db.flush()
    return rel


# ── Notes coach sur client ────────────────────────────────────────────────────

async def get_or_create_note(
    db: AsyncSession, coach_id: uuid.UUID, client_id: uuid.UUID
) -> CoachClientNote:
    q = select(CoachClientNote).where(
        CoachClientNote.coach_id == coach_id,
        CoachClientNote.client_id == client_id,
    )
    result = await db.execute(q)
    note = result.scalar_one_or_none()
    if note is None:
        note = CoachClientNote(
            id=uuid.uuid4(), coach_id=coach_id, client_id=client_id
        )
        db.add(note)
        await db.flush()
    return note


async def update_note(
    db: AsyncSession, note: CoachClientNote, content: str | None
) -> CoachClientNote:
    note.content = content
    await db.flush()
    return note

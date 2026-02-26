"""Repository templates de messages d'annulation — B1-32."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cancellation_message_template import (
    CancellationMessageTemplate,
    TEMPLATE_VARIABLES,
    DEFAULT_TEMPLATE_TITLE,
    DEFAULT_TEMPLATE_BODY,
)
from app.schemas.cancellation_template import _extract_variables

MAX_TEMPLATES_PER_COACH = 5


class MaxTemplatesReachedError(Exception):
    pass


class LastTemplateError(Exception):
    pass


async def list_by_coach(
    db: AsyncSession, coach_id: uuid.UUID
) -> list[CancellationMessageTemplate]:
    q = (
        select(CancellationMessageTemplate)
        .where(CancellationMessageTemplate.coach_id == coach_id)
        .order_by(CancellationMessageTemplate.position)
    )
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_by_id_and_coach(
    db: AsyncSession, template_id: uuid.UUID, coach_id: uuid.UUID
) -> CancellationMessageTemplate | None:
    q = select(CancellationMessageTemplate).where(
        CancellationMessageTemplate.id == template_id,
        CancellationMessageTemplate.coach_id == coach_id,
    )
    result = await db.execute(q)
    return result.scalar_one_or_none()


async def count_by_coach(db: AsyncSession, coach_id: uuid.UUID) -> int:
    q = select(func.count()).where(
        CancellationMessageTemplate.coach_id == coach_id
    )
    result = await db.execute(q)
    return result.scalar_one()


async def create(
    db: AsyncSession,
    coach_id: uuid.UUID,
    title: str,
    body: str,
    *,
    is_default: bool = False,
    position: int | None = None,
) -> CancellationMessageTemplate:
    """Crée un template. Lève MaxTemplatesReachedError si max 5 atteint."""
    count = await count_by_coach(db, coach_id)
    if count >= MAX_TEMPLATES_PER_COACH:
        raise MaxTemplatesReachedError(
            f"Maximum {MAX_TEMPLATES_PER_COACH} templates par coach"
        )
    if position is None:
        position = count + 1

    obj = CancellationMessageTemplate(
        id=uuid.uuid4(),
        coach_id=coach_id,
        title=title,
        body=body,
        variables_used=_extract_variables(body),
        is_default=is_default,
        position=position,
    )
    db.add(obj)
    await db.flush()
    return obj


async def create_default(
    db: AsyncSession, coach_id: uuid.UUID
) -> CancellationMessageTemplate:
    """Seed automatique : crée le template 'Maladie' par défaut."""
    return await create(
        db, coach_id,
        title=DEFAULT_TEMPLATE_TITLE,
        body=DEFAULT_TEMPLATE_BODY,
        is_default=True,
        position=1,
    )


async def update(
    db: AsyncSession,
    template: CancellationMessageTemplate,
    **kwargs: Any,
) -> CancellationMessageTemplate:
    for k, v in kwargs.items():
        setattr(template, k, v)
    # Re-calculer variables_used si body change
    if "body" in kwargs:
        template.variables_used = _extract_variables(kwargs["body"])
    await db.flush()
    return template


async def delete(
    db: AsyncSession, template: CancellationMessageTemplate
) -> None:
    """Supprime un template. Lève LastTemplateError s'il est le dernier."""
    count = await count_by_coach(db, template.coach_id)
    if count <= 1:
        raise LastTemplateError("Impossible de supprimer le dernier template")
    await db.delete(template)
    await db.flush()


async def reorder(
    db: AsyncSession,
    coach_id: uuid.UUID,
    items: list[dict],  # [{"id": UUID, "position": int}, ...]
) -> list[CancellationMessageTemplate]:
    """Met à jour les positions des templates.
    items = [{"id": uuid, "position": int}]

    Raises:
        ValueError si un ID n'appartient pas à ce coach.
    """
    updated = []
    for item in items:
        t = await get_by_id_and_coach(db, item["id"], coach_id)
        if t is None:
            raise ValueError(f"Template {item['id']} introuvable pour ce coach")
        t.position = item["position"]
        updated.append(t)
    await db.flush()
    # Retourner trié par position croissante
    return sorted(updated, key=lambda x: x.position)

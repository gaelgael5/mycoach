"""Service — Paramètres de santé, logs, partage."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_log import HealthLog
from app.models.health_parameter import HealthParameter
from app.models.health_sharing_setting import HealthSharingSetting
from app.repositories import health_repository
from app.schemas.health import HealthLogCreate, HealthParameterCreate, HealthParameterUpdate, HealthSharingItem


class LogNotFoundError(Exception):
    """Le log de mesure demandé n'existe pas."""


class ParameterNotFoundError(Exception):
    """Le paramètre de santé demandé n'existe pas."""


async def get_active_parameters(db: AsyncSession) -> list[HealthParameter]:
    return await health_repository.get_parameters(db, active_only=True)


async def get_all_parameters(db: AsyncSession) -> list[HealthParameter]:
    return await health_repository.get_parameters(db, active_only=False)


async def log_measurement(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: HealthLogCreate,
) -> HealthLog:
    param = await health_repository.get_parameter_by_id(db, data.parameter_id)
    if param is None:
        raise HTTPException(status_code=422, detail="Paramètre de santé inconnu")
    if not param.active:
        raise HTTPException(status_code=422, detail="Paramètre de santé inactif")
    return await health_repository.create_log(
        db,
        user_id=user_id,
        parameter_id=data.parameter_id,
        value=data.value,
        note=data.note,
        source=data.source,
        logged_at=data.logged_at,
    )


async def get_my_logs(
    db: AsyncSession,
    user_id: uuid.UUID,
    param_id: Optional[uuid.UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> list[HealthLog]:
    return await health_repository.get_logs(db, user_id, param_id, from_date, to_date)


async def delete_log(
    db: AsyncSession,
    user_id: uuid.UUID,
    log_id: uuid.UUID,
) -> None:
    deleted = await health_repository.delete_log(db, log_id, user_id)
    if not deleted:
        raise LogNotFoundError(f"Log {log_id} introuvable pour cet utilisateur")


async def get_my_sharing(
    db: AsyncSession,
    user_id: uuid.UUID,
    coach_id: uuid.UUID,
) -> list[dict]:
    """Retourne TOUS les params actifs avec shared=True/False pour ce coach."""
    params = await health_repository.get_parameters(db, active_only=True)
    settings = await health_repository.get_sharing_settings(db, user_id, coach_id)
    settings_map = {s.parameter_id: s.shared for s in settings}
    return [
        {
            "parameter_id": p.id,
            "shared": settings_map.get(p.id, True),  # défaut = partagé
        }
        for p in params
    ]


async def update_sharing(
    db: AsyncSession,
    user_id: uuid.UUID,
    coach_id: uuid.UUID,
    updates: list[HealthSharingItem],
) -> list[HealthSharingSetting]:
    results = []
    for item in updates:
        setting = await health_repository.upsert_sharing(
            db, user_id, coach_id, item.parameter_id, item.shared
        )
        results.append(setting)
    return results


async def get_client_logs(
    db: AsyncSession,
    coach_id: uuid.UUID,
    client_id: uuid.UUID,
    param_id: Optional[uuid.UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> list[HealthLog]:
    """Retourne les logs d'un client, filtrés par les paramètres partagés avec ce coach."""
    all_logs = await health_repository.get_logs(db, client_id, param_id, from_date, to_date)
    # Filter by sharing settings
    filtered = []
    for log in all_logs:
        is_shared = await health_repository.is_parameter_shared(
            db, client_id, coach_id, log.parameter_id
        )
        if is_shared:
            filtered.append(log)
    return filtered


async def admin_create_parameter(
    db: AsyncSession,
    data: HealthParameterCreate,
) -> HealthParameter:
    return await health_repository.create_parameter(
        db,
        slug=data.slug,
        label=data.label,
        unit=data.unit,
        data_type=data.data_type,
        category=data.category,
        position=data.position,
    )


async def admin_update_parameter(
    db: AsyncSession,
    param_id: uuid.UUID,
    data: HealthParameterUpdate,
) -> HealthParameter:
    param = await health_repository.get_parameter_by_id(db, param_id)
    if param is None:
        raise ParameterNotFoundError(f"Paramètre {param_id} introuvable")
    update_fields = data.model_dump(exclude_none=True)
    return await health_repository.update_parameter(db, param, **update_fields)


async def admin_delete_parameter(
    db: AsyncSession,
    param_id: uuid.UUID,
) -> HealthParameter:
    """Soft delete — active=False."""
    param = await health_repository.get_parameter_by_id(db, param_id)
    if param is None:
        raise ParameterNotFoundError(f"Paramètre {param_id} introuvable")
    return await health_repository.soft_delete_parameter(db, param)

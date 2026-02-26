"""Router actions en masse (bulk cancel + SMS broadcast) — B2-34."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_coach
from app.database import get_db
from app.models.user import User
from app.services.bulk_cancel_service import bulk_cancel_bookings, BulkCancelAuthError

router = APIRouter(prefix="/coaches", tags=["bulk-actions"])


# ── Bulk cancel ────────────────────────────────────────────────────────────────

@router.post("/bookings/bulk-cancel")
async def bulk_cancel(
    data: dict,
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.schemas.sms import BulkCancelRequest, BulkCancelResponse
        req = BulkCancelRequest(**data)
        result = await bulk_cancel_bookings(
            db, current_user,
            req.booking_ids,
            template_id=req.template_id,
            custom_message=req.custom_message,
            send_sms=req.send_sms,
        )
        await db.commit()
        return BulkCancelResponse(
            cancelled_count=result.cancelled_count,
            sms_sent_count=result.sms_sent_count,
            sms_failed_count=result.sms_failed_count,
            failed_clients=result.failed_clients,
        )
    except BulkCancelAuthError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ImportError:
        raise HTTPException(status_code=503, detail="Module SMS non disponible")


# ── SMS logs ───────────────────────────────────────────────────────────────────

@router.get("/sms/logs")
async def sms_logs(
    status: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_coach),
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.repositories.sms_log_repository import list_by_coach
        items, total = await list_by_coach(
            db, current_user.id, status=status, offset=offset, limit=limit
        )
        return {"items": items, "total": total, "offset": offset, "limit": limit}
    except ImportError:
        return {"items": [], "total": 0, "offset": offset, "limit": limit}

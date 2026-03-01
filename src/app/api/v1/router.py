"""API v1 aggregated router."""
from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.clients import router as clients_router
from app.api.v1.coach import router as coach_router
from app.api.v1.programs import router as programs_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.tracking import router as tracking_router
from app.api.v1.conversations import router as conversations_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(clients_router)
api_v1_router.include_router(coach_router)
api_v1_router.include_router(programs_router)
api_v1_router.include_router(sessions_router)
api_v1_router.include_router(tracking_router)
api_v1_router.include_router(conversations_router)

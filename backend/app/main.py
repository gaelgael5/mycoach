"""
Point d'entrée FastAPI — MyCoach Backend.

Configure : CORS, security headers, rate limiting, exception handlers, routers.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import get_settings
from app.database import engine
from app.routers import auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


# ---------------------------------------------------------------------------
# Rate limiter (slowapi)
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)


# ---------------------------------------------------------------------------
# Lifespan (startup/shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 MyCoach Backend démarrage (env=%s)", settings.ENVIRONMENT)
    yield
    await engine.dispose()
    logger.info("👋 MyCoach Backend arrêt propre")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="MyCoach API",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
    lifespan=lifespan,
)
app.state.limiter = limiter


# ---------------------------------------------------------------------------
# CORS — origines strictes (pas de * en production)
# ---------------------------------------------------------------------------

allowed_origins = (
    [settings.FRONTEND_URL]
    if settings.is_production
    else ["http://localhost:3000", "http://localhost:8000", settings.FRONTEND_URL]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Security headers — middleware ASGI pur (pas de BaseHTTPMiddleware)
# BaseHTTPMiddleware crée de nouvelles tâches asyncio incompatibles avec
# asyncpg en mode test (connexion liée à un event loop spécifique).
# ---------------------------------------------------------------------------

class _SecurityHeadersMiddleware:
    """Injecte les security headers sans créer de nouvelles tâches asyncio."""

    def __init__(self, app: ASGIApp, is_production: bool = False) -> None:
        self.app = app
        self.is_production = is_production

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def _send(message):
            if message["type"] == "http.response.start":
                extra = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                ]
                if self.is_production:
                    extra.append(
                        (b"strict-transport-security", b"max-age=63072000; includeSubDomains")
                    )
                message = {**message, "headers": list(message.get("headers", [])) + extra}
            await send(message)

        await self.app(scope, receive, _send)


app.add_middleware(_SecurityHeadersMiddleware, is_production=settings.is_production)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Erreur non gérée : %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "server_error"},  # clé i18n, jamais de stack trace
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
# Phase 1+ : coaches, clients, gyms, bookings, etc. ajoutés ici


# ---------------------------------------------------------------------------
# GET /health — sans authentification
# ---------------------------------------------------------------------------

@app.get("/health", tags=["system"])
async def health():
    """Vérifie que l'API et la base de données sont opérationnelles."""
    from app.database import AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error("DB health check failed: %s", e)
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }

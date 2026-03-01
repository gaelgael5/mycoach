"""MyCoach — FastAPI entry point (v2, async + PostgreSQL)."""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db.base import engine, Base
from app.models.tables import *  # noqa: F401,F403
from app.api.v1.router import api_v1_router

# ── Structured logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("mycoach")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MyCoach backend…")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready.")
    yield
    logger.info("Shutting down MyCoach backend.")


app = FastAPI(title="MyCoach", version="1.0.0", lifespan=lifespan)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global error handlers ───────────────────────────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": True, "detail": exc.errors(), "status_code": 422},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": True, "detail": "Internal server error", "status_code": 500},
    )


# ── Routes ───────────────────────────────────────────────────────────
app.include_router(api_v1_router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "mycoach-backend", "version": "1.0.0"}


# Keep legacy health check
@app.get("/health")
async def health_legacy():
    return {"status": "ok"}

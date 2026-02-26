# ─────────────────────────────────────────────────────────────────────────────
# MyCoach API — Dockerfile PRODUCTION
# Multi-stage build : builder → runtime minimal
# Image finale : ~200MB, sans outils de dev
# ─────────────────────────────────────────────────────────────────────────────

# ─── Stage 1 : Builder ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update -q && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ─── Stage 2 : Runtime ────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL maintainer="MyCoach Team"
LABEL description="MyCoach FastAPI — image production"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    APP_ENV=production

WORKDIR /app

# Runtime : curl (healthcheck) + libpq (asyncpg)
RUN apt-get update -q && \
    apt-get install -y --no-install-recommends \
        curl \
        libpq5 \
    && rm -rf /var/lib/apt/lists/* && \
    # Utilisateur non-root
    groupadd -r mycoach && \
    useradd -r -g mycoach -s /bin/bash -d /app mycoach

# Installer les wheels depuis le builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && \
    rm -rf /wheels

# Copier le code application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Répertoires writable
RUN mkdir -p /app/uploads /app/logs && \
    chown -R mycoach:mycoach /app

USER mycoach

EXPOSE 8000

# Healthcheck intégré
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entrypoint : migrations puis démarrage production
CMD ["sh", "-c", \
    "alembic upgrade head && \
     uvicorn app.main:app \
       --host 0.0.0.0 \
       --port 8000 \
       --workers 2 \
       --log-level info \
       --access-log"]

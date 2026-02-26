"""
Fixtures pytest — isolation par TRUNCATE entre chaque test.

L'approche "outer transaction + savepoint" génère des conflits asyncpg
(Future attached to a different loop) quand ASGITransport envoie des requêtes.
Solution retenue : session propre par requête + DELETE avant chaque test.

Prérequis :
    sudo -u postgres psql -c "CREATE USER mycoach WITH PASSWORD 'mycoach_test';"
    sudo -u postgres psql -c "CREATE DATABASE mycoach_test OWNER mycoach;"
    sudo -u postgres psql -d mycoach_test -c "
        CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
        CREATE EXTENSION IF NOT EXISTS unaccent;
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
    "
"""
import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.repositories.api_key_repository import api_key_repository
from app.repositories.user_repository import user_repository

settings = get_settings()

# Engine et SessionLocal de test
_test_engine = create_async_engine(settings.DATABASE_URL, echo=False)
_TestSession = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


# ---------------------------------------------------------------------------
# Tables : create once (session), drop after all tests
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session")
async def create_tables():
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _test_engine.dispose()


# ---------------------------------------------------------------------------
# Nettoyage avant chaque test (DELETE dans l'ordre inverse des FK)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(autouse=True)
async def clean_tables(create_tables):
    """Vide toutes les tables avant chaque test — isolation garantie."""
    async with _test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


# ---------------------------------------------------------------------------
# db : session fraîche par test (pas de partage de connexion)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def db(clean_tables) -> AsyncGenerator[AsyncSession, None]:
    """Session DB indépendante — chaque test commence sur une base propre (via clean_tables)."""
    async with _TestSession() as session:
        yield session


# ---------------------------------------------------------------------------
# Client HTTP — override get_db avec une session indépendante
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def client(clean_tables) -> AsyncGenerator[AsyncClient, None]:
    """
    Client HTTP avec sa propre session DB.
    NB : utilise une session distincte de la fixture db ci-dessus —
    les données écrites via client.post(...) sont donc visibles dans db
    uniquement après flush/commit.
    """
    async def _override():
        async with _TestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Fixture db+client combinée (partage la même session)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def db_and_client(create_tables):
    """
    db + client partageant la même session.
    Utiliser quand le test a besoin de préparer des données ET de faire des requêtes HTTP.
    """
    session = _TestSession()
    calls = {"count": 0}

    async def _override():
        yield session
        await session.flush()

    app.dependency_overrides[get_db] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield session, c
    await session.commit()
    await session.close()
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Utilisateurs pré-créés (utilisent db_and_client pour la cohérence)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def coach_user(db: AsyncSession):
    """Coach vérifié, créé dans la session `db`."""
    user = await user_repository.create(
        db, first_name="Coach", last_name="Test",
        email=f"coach_{uuid.uuid4().hex[:8]}@test.com",
        role="coach", password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    await db.commit()
    return user


@pytest_asyncio.fixture()
async def client_user(db: AsyncSession):
    """Client vérifié, créé dans la session `db`."""
    user = await user_repository.create(
        db, first_name="Client", last_name="Test",
        email=f"client_{uuid.uuid4().hex[:8]}@test.com",
        role="client", password_plain="Password1",
    )
    await user_repository.mark_email_verified(db, user)
    await db.commit()
    return user


@pytest_asyncio.fixture()
async def coach_api_key(coach_user, db: AsyncSession) -> str:
    plain_key, _ = await api_key_repository.create(db, coach_user.id, "test-device")
    await db.commit()
    return plain_key


@pytest_asyncio.fixture()
async def client_api_key(client_user, db: AsyncSession) -> str:
    plain_key, _ = await api_key_repository.create(db, client_user.id, "test-device")
    await db.commit()
    return plain_key

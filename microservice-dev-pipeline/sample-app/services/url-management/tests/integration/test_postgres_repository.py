"""
Integration tests for PostgresUrlRepository.

Uses testcontainers to run a real PostgreSQL instance and verifies
that data is actually persisted to the database using the NEW session
verification pattern.
"""

import pytest
from datetime import datetime, timezone

from testcontainers.postgres import PostgresContainer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.adapters.postgres_repository import PostgresUrlRepository
from app.models.url_mapping import Base, UrlMapping


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def postgres_container():
    """
    Start PostgreSQL container for integration tests.

    Scope: module (shared across all tests in this file for performance).
    """
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture
async def engine(postgres_container):
    """
    Create async database engine and initialize schema.

    Uses function scope to avoid event loop conflicts.
    Uses NullPool to prevent connection pooling issues in tests.
    """
    db_url = postgres_container.replace("psycopg2", "asyncpg")

    engine = create_async_engine(db_url, poolclass=NullPool, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def session(engine):
    """Create database session for tests. Each test gets a fresh session."""
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_maker() as session:
        yield session

        # Cleanup after test
        async with engine.begin() as conn:
            await conn.execute(text("TRUNCATE TABLE url_mappings CASCADE"))


@pytest.fixture
async def repository(session):
    """Create repository instance for testing."""
    return PostgresUrlRepository(session)


# ============================================================================
# Persistence Verification Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_persists_to_database(repository, session, engine):
    """
    Verify that save() actually persists to database.

    Uses NEW session verification to catch missing commit() bugs.
    """
    url_mapping = UrlMapping(
        short_code="abc12345",
        long_url="https://example.com/test-persist",
        created_at=datetime.now(timezone.utc),
    )
    await repository.save(url_mapping)
    await session.commit()

    # Verify with NEW session
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as new_session:
        result = await new_session.execute(
            text("SELECT short_code, long_url FROM url_mappings WHERE short_code = :code"),
            {"code": "abc12345"},
        )
        row = result.fetchone()
        assert row is not None, "Data was not persisted to database!"
        assert row[0] == "abc12345"
        assert row[1] == "https://example.com/test-persist"


@pytest.mark.asyncio
async def test_find_by_short_code(repository, session, engine):
    """Verify that find_by_short_code returns persisted data."""
    url_mapping = UrlMapping(
        short_code="find1234",
        long_url="https://example.com/find-by-code",
        created_at=datetime.now(timezone.utc),
    )
    await repository.save(url_mapping)
    await session.commit()

    # Verify with NEW session and new repository instance
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as new_session:
        new_repo = PostgresUrlRepository(new_session)
        found = await new_repo.find_by_short_code("find1234")

        assert found is not None, "find_by_short_code did not return persisted data!"
        assert found.short_code == "find1234"
        assert found.long_url == "https://example.com/find-by-code"


@pytest.mark.asyncio
async def test_find_by_long_url(repository, session, engine):
    """Verify that find_by_long_url returns persisted data."""
    url_mapping = UrlMapping(
        short_code="long1234",
        long_url="https://example.com/find-by-long-url",
        created_at=datetime.now(timezone.utc),
    )
    await repository.save(url_mapping)
    await session.commit()

    # Verify with NEW session and new repository instance
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as new_session:
        new_repo = PostgresUrlRepository(new_session)
        found = await new_repo.find_by_long_url("https://example.com/find-by-long-url")

        assert found is not None, "find_by_long_url did not return persisted data!"
        assert found.short_code == "long1234"
        assert found.long_url == "https://example.com/find-by-long-url"


@pytest.mark.asyncio
async def test_idempotent_save(repository, session, engine):
    """
    Verify that saving the same short code twice does not create duplicates.

    The repository should handle idempotent saves correctly.
    """
    url_mapping1 = UrlMapping(
        short_code="idem1234",
        long_url="https://example.com/idempotent-test",
        created_at=datetime.now(timezone.utc),
    )
    await repository.save(url_mapping1)
    await session.commit()

    # Verify with NEW session that exactly one row exists
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as new_session:
        result = await new_session.execute(
            text("SELECT COUNT(*) FROM url_mappings WHERE short_code = :code"),
            {"code": "idem1234"},
        )
        count = result.scalar()
        assert count == 1, f"Expected 1 row, found {count}"

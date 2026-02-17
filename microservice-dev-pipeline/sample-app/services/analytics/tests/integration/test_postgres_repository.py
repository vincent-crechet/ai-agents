"""
Integration tests for PostgresAnalyticsRepository.

Uses testcontainers to run tests against a real PostgreSQL database.
Follows the NEW session verification pattern to catch missing commit() bugs.
"""

import pytest
from datetime import datetime, timezone

from testcontainers.postgres import PostgresContainer
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import NullPool

from app.adapters.postgres_repository import PostgresAnalyticsRepository
from app.models.url_access_stats import Base, UrlAccessStats
from app.services.analytics_service import AnalyticsService
from architecture.contracts.common import UrlAccessedEvent


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
    """
    Create database session for tests.

    Each test gets a fresh session. Tables are truncated after each test.
    """
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_maker() as session:
        yield session

    # Cleanup after test
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE url_access_stats CASCADE"))


@pytest.fixture
async def repository(session) -> PostgresAnalyticsRepository:
    """Create repository instance for testing."""
    return PostgresAnalyticsRepository(session)


# ============================================================================
# Persistence Verification Tests
# ============================================================================


@pytest.mark.asyncio
async def test_increment_access_count_persists(repository, session, engine):
    """
    Verify that increment_access_count actually persists to database.

    Pattern: Write via repository, commit, verify with NEW session.
    """
    await repository.increment_access_count(
        short_code="test1", long_url="https://test1.com"
    )
    await session.commit()

    # Verify with NEW session
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_maker() as new_session:
        stmt = select(UrlAccessStats).where(
            UrlAccessStats.short_code == "test1"
        )
        result = await new_session.execute(stmt)
        found = result.scalar_one_or_none()

        assert found is not None, "Data was not persisted to database!"
        assert found.short_code == "test1"
        assert found.long_url == "https://test1.com"
        assert found.access_count == 1


@pytest.mark.asyncio
async def test_increment_existing_url_persists(repository, session, engine):
    """
    Verify that incrementing an existing URL updates the count in the database.
    """
    await repository.increment_access_count(
        short_code="test2", long_url="https://test2.com"
    )
    await session.commit()

    # Increment again
    await repository.increment_access_count(
        short_code="test2", long_url="https://test2.com"
    )
    await session.commit()

    # Verify with NEW session
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_maker() as new_session:
        stmt = select(UrlAccessStats).where(
            UrlAccessStats.short_code == "test2"
        )
        result = await new_session.execute(stmt)
        found = result.scalar_one_or_none()

        assert found is not None
        assert found.access_count == 2


@pytest.mark.asyncio
async def test_get_top_urls_returns_correct_ranking(
    repository, session, engine
):
    """
    Verify that get_top_urls returns URLs ranked by access count descending.
    """
    # Create URL A with 3 accesses
    for _ in range(3):
        await repository.increment_access_count(
            short_code="rank_a", long_url="https://a.com"
        )

    # Create URL B with 1 access
    await repository.increment_access_count(
        short_code="rank_b", long_url="https://b.com"
    )

    # Create URL C with 2 accesses
    for _ in range(2):
        await repository.increment_access_count(
            short_code="rank_c", long_url="https://c.com"
        )

    await session.commit()

    # Verify with NEW session and NEW repository
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_maker() as new_session:
        new_repo = PostgresAnalyticsRepository(new_session)
        results = await new_repo.get_top_urls(limit=10)

        assert len(results) == 3
        assert results[0].short_code == "rank_a"
        assert results[0].access_count == 3
        assert results[1].short_code == "rank_c"
        assert results[1].access_count == 2
        assert results[2].short_code == "rank_b"
        assert results[2].access_count == 1


@pytest.mark.asyncio
async def test_event_handler_persists_changes(engine):
    """
    CRITICAL: Verify that event handlers persist changes to the database.

    This test creates a service with a real repository, handles an event,
    and verifies the data was persisted using a NEW session.
    """
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Handle event with service using real repository
    async with session_maker() as session:
        repository = PostgresAnalyticsRepository(session)
        service = AnalyticsService(repository=repository)

        event = UrlAccessedEvent(
            short_code="event_test",
            long_url="https://event-test.com",
            accessed_at=datetime.now(timezone.utc),
        )
        await service.handle_url_accessed(event)

    # Verify with NEW session
    async with session_maker() as new_session:
        stmt = select(UrlAccessStats).where(
            UrlAccessStats.short_code == "event_test"
        )
        result = await new_session.execute(stmt)
        found = result.scalar_one_or_none()

        assert found is not None, "Event handler did not persist changes!"
        assert found.short_code == "event_test"
        assert found.long_url == "https://event-test.com"
        assert found.access_count == 1

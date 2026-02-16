"""
Template for repository integration tests.

CRITICAL: These tests verify that data is actually PERSISTED to the database,
not just cached in the session. Always verify with a NEW session!

This pattern catches missing commit() bugs.
"""

import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from datetime import datetime, timezone

# Import your repository and models
# from app.adapters.postgres_repository import PostgresRepository, Base


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def postgres_container():
    """
    Start PostgreSQL container for integration tests.

    Scope: module (shared across all tests in this file for performance)
    """
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture
async def engine(postgres_container):
    """
    Create async database engine and initialize schema.

    IMPORTANT: Use function scope (not module) to avoid event loop conflicts.
    """
    # Convert psycopg2 URL to asyncpg
    db_url = postgres_container.replace("psycopg2", "asyncpg")

    # Use NullPool to prevent connection pooling issues in tests
    engine = create_async_engine(db_url, poolclass=NullPool, echo=False)

    # Create tables
    async with engine.begin() as conn:
        # Import your Base here
        # await conn.run_sync(Base.metadata.create_all)
        pass

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def session(engine):
    """
    Create database session for tests.

    Each test gets a fresh session.
    """
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_maker() as session:
        yield session

        # Cleanup after test (truncate tables)
        # Note: Use a separate connection to avoid "operation in progress" errors
        async with engine.begin() as conn:
            # await conn.run_sync(lambda sync_conn: sync_conn.execute(text("TRUNCATE TABLE your_table CASCADE")))
            pass


@pytest.fixture
async def repository(session):
    """Create repository instance for testing."""
    # return PostgresRepository(session)
    pass


# ============================================================================
# Persistence Verification Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_persists_to_database(repository, session, engine):
    """
    CRITICAL TEST: Verify that create() actually persists to database.

    This test pattern catches missing commit() bugs!

    Pattern:
    1. Create data via repository
    2. Commit the session
    3. ✅ Query with a NEW session to verify persistence
    """
    # Step 1: Create data
    # result = await repository.create(
    #     field1="value1",
    #     field2="value2"
    # )
    # created_id = result.id

    # Step 2: Commit the transaction
    await session.commit()

    # Step 3: ✅ CRITICAL - Verify with NEW session
    # If commit() is missing, this will fail!
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as new_session:
        # Query the database with fresh session
        # from sqlalchemy import select
        # from app.adapters.postgres_repository import YourModel

        # stmt = select(YourModel).where(YourModel.id == created_id)
        # result = await new_session.execute(stmt)
        # found = result.scalar_one_or_none()

        # assert found is not None, "Data was not persisted to database!"
        # assert found.field1 == "value1"
        pass


@pytest.mark.asyncio
async def test_update_persists_to_database(repository, session, engine):
    """
    Verify that update() actually persists changes.

    This catches bugs where flush() is called but not commit().
    """
    # Create initial data
    # result = await repository.create(field1="original")
    # item_id = result.id
    await session.commit()

    # Update the data
    # await repository.update(item_id, field1="updated")
    await session.commit()

    # ✅ Verify with NEW session
    session_maker = async_sessionmaker(engine, class_=AsyncSession)
    async with session_maker() as new_session:
        # Query and verify update persisted
        # stmt = select(YourModel).where(YourModel.id == item_id)
        # result = await new_session.execute(stmt)
        # found = result.scalar_one()

        # assert found.field1 == "updated", "Update was not persisted!"
        pass


@pytest.mark.asyncio
async def test_delete_persists_to_database(repository, session, engine):
    """Verify that delete() actually removes from database."""
    # Create data
    # result = await repository.create(field1="to_delete")
    # item_id = result.id
    await session.commit()

    # Delete the data
    # await repository.delete(item_id)
    await session.commit()

    # ✅ Verify with NEW session
    session_maker = async_sessionmaker(engine, class_=AsyncSession)
    async with session_maker() as new_session:
        # Verify deletion persisted
        # stmt = select(YourModel).where(YourModel.id == item_id)
        # result = await new_session.execute(stmt)
        # found = result.scalar_one_or_none()

        # assert found is None, "Delete was not persisted!"
        pass


@pytest.mark.asyncio
async def test_query_returns_persisted_data_only(repository, session, engine):
    """
    Verify that queries return data from database, not just session cache.

    This is critical for ensuring repository doesn't rely on session cache.
    """
    # Create some data in first session
    # await repository.create(field1="item1")
    # await repository.create(field1="item2")
    await session.commit()

    # ✅ Query with a DIFFERENT repository instance (new session)
    session_maker = async_sessionmaker(engine, class_=AsyncSession)
    async with session_maker() as new_session:
        # new_repo = PostgresRepository(new_session)
        # results = await new_repo.find_all()

        # assert len(results) == 2, "Repository should return persisted data"
        pass


# ============================================================================
# Event Handler Persistence Tests (For Event-Driven Services)
# ============================================================================

@pytest.mark.asyncio
async def test_event_handler_persists_changes(engine):
    """
    CRITICAL for services that consume events (EVENTS_CONSUMED not empty).

    Verify that event handlers actually persist their changes to database.
    This catches missing commit() bugs in event handlers.
    """
    # Create service with real repository
    session_maker = async_sessionmaker(engine, class_=AsyncSession)
    async with session_maker() as session:
        # repo = PostgresRepository(session)
        # service = YourService(repo, mock_message_broker)

        # Create and handle an event
        # event = YourEvent(field1="value1", timestamp=datetime.now(timezone.utc))
        # await service.handle_event(event)

        # Note: If service doesn't commit internally, do it here
        # await session.commit()
        pass

    # ✅ CRITICAL: Verify with NEW session (different from handler's session!)
    async with session_maker() as new_session:
        # Query database to verify event was processed and persisted
        # from sqlalchemy import select
        # stmt = select(YourModel).where(YourModel.field1 == "value1")
        # result = await new_session.execute(stmt)
        # found = result.scalar_one_or_none()

        # assert found is not None, "Event handler did not persist changes!"
        pass


# ============================================================================
# Transaction and Concurrency Tests
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_updates_handled_correctly(repository, session, engine):
    """
    Test that concurrent updates don't cause data loss.

    This catches transaction isolation issues.
    """
    # Create initial data
    # result = await repository.create(counter=0)
    # item_id = result.id
    await session.commit()

    # Simulate concurrent updates with separate sessions
    session_maker = async_sessionmaker(engine, class_=AsyncSession)

    # Update 1 in first session
    async with session_maker() as session1:
        # repo1 = PostgresRepository(session1)
        # await repo1.increment_counter(item_id)
        # await session1.commit()
        pass

    # Update 2 in second session
    async with session_maker() as session2:
        # repo2 = PostgresRepository(session2)
        # await repo2.increment_counter(item_id)
        # await session2.commit()
        pass

    # Verify both updates persisted
    async with session_maker() as verify_session:
        # stmt = select(YourModel).where(YourModel.id == item_id)
        # result = await verify_session.execute(stmt)
        # found = result.scalar_one()

        # assert found.counter == 2, "Concurrent updates not handled correctly!"
        pass


# ============================================================================
# Common Patterns and Best Practices
# ============================================================================

"""
TESTING PATTERNS SUMMARY:

1. ✅ ALWAYS verify with NEW session
   Bad:  await repo.create(...); result = await repo.find(...)
   Good: await repo.create(...); await session.commit(); <new session> result = await repo.find(...)

2. ✅ ALWAYS commit after write operations (in test or repository)
   Bad:  await repo.create(...); <query immediately>
   Good: await repo.create(...); await session.commit(); <query>

3. ✅ Use NullPool for test engines (prevents connection issues)
   engine = create_async_engine(url, poolclass=NullPool)

4. ✅ Use function scope for async engine fixture (prevents event loop issues)
   @pytest.fixture(scope="function")  # NOT "module"

5. ✅ Clean up with separate connection (prevents "operation in progress" errors)
   async with engine.begin() as conn:
       await conn.run_sync(lambda sync_conn: ...)

6. ✅ Test event handlers with NEW session (catches missing commits)
   await handler(event); <new session> verify_in_db()

WHAT THESE TESTS CATCH:

- ❌ Missing commit() calls (flush but no commit)
- ❌ Wrong table names (query fails on non-existent table)
- ❌ Schema mismatches (column name differences)
- ❌ Transaction issues (nested transactions, deadlocks)
- ❌ Session cache dependencies (relying on cache instead of DB)
- ❌ Event handler persistence bugs (missing commits in handlers)

WHY NEW SESSION IS CRITICAL:

If you query with the same session, you're reading from the session cache,
not the actual database. This means missing commit() bugs go undetected!

Example:
  # ❌ Bad - reads from session cache:
  await repo.create(...)
  result = await repo.find(...)  # Finds it even without commit!

  # ✅ Good - reads from database:
  await repo.create(...)
  await session.commit()
  <create new session>
  result = await repo.find(...)  # Only finds it if committed!
"""

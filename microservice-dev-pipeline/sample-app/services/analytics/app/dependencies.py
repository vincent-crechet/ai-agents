"""
Dependency injection wiring for the analytics service.

Provides FastAPI Depends callables for injecting service dependencies.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.adapters.postgres_repository import PostgresAnalyticsRepository
from app.services.analytics_service import AnalyticsService

engine = create_async_engine(settings.database_url, echo=False)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session with automatic cleanup."""
    async with async_session_factory() as session:
        yield session


async def get_repository(
    session: AsyncSession = None,
) -> PostgresAnalyticsRepository:
    """Provide a repository instance."""
    return PostgresAnalyticsRepository(session)


async def get_analytics_service() -> AsyncGenerator[AnalyticsService, None]:
    """Provide an analytics service instance with injected dependencies."""
    async with async_session_factory() as session:
        repository = PostgresAnalyticsRepository(session)
        yield AnalyticsService(repository=repository)

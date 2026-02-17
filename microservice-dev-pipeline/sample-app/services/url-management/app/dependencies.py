"""
Dependency injection wiring for the url-management service.

Provides FastAPI dependency functions that wire together ports and adapters
at runtime. This is the composition root of the application.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.adapters.postgres_repository import PostgresUrlRepository
from app.adapters.rabbitmq_broker import RabbitMQBroker
from app.config import get_settings
from app.services.url_service import UrlManagementService

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False)
session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

broker = RabbitMQBroker(
    rabbitmq_url=settings.rabbitmq_url,
    exchange_name=settings.rabbitmq_exchange,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session with automatic cleanup."""
    async with session_maker() as session:
        yield session


async def get_url_service() -> AsyncGenerator[UrlManagementService, None]:
    """Provide a fully wired UrlManagementService instance."""
    async with session_maker() as session:
        repository = PostgresUrlRepository(session)
        service = UrlManagementService(
            repository=repository,
            message_broker=broker,
            base_url=settings.base_url,
        )
        yield service

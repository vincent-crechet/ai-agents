"""
FastAPI application entry point for the analytics service.

Configures the application, exception handlers, and lifespan events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from architecture.contracts.common import UrlAccessedEvent
from app.adapters.postgres_repository import PostgresAnalyticsRepository
from app.adapters.rabbitmq_broker import RabbitMQBroker
from app.api.stats import router as stats_router
from app.config import settings
from app.dependencies import async_session_factory, engine
from app.exceptions.analytics_exceptions import InvalidLimitError
from app.models.url_access_stats import Base
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Connects to RabbitMQ and subscribes to UrlAccessedEvent on startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    broker = RabbitMQBroker(
        rabbitmq_url=settings.rabbitmq_url,
        exchange_name=settings.rabbitmq_exchange,
        service_name=settings.service_name,
    )

    try:
        await broker.connect()

        async def handle_event(event: UrlAccessedEvent) -> None:
            """Handle incoming URL accessed events with a fresh session."""
            async with async_session_factory() as session:
                repository = PostgresAnalyticsRepository(session)
                service = AnalyticsService(repository=repository)
                await service.handle_url_accessed(event)

        await broker.subscribe(UrlAccessedEvent, handle_event)
        logger.info("Analytics service started, listening for events")
    except Exception as e:
        logger.warning(
            f"Could not connect to RabbitMQ: {e}. "
            "Service will run without event consumption.",
            extra={"error": str(e)},
        )

    yield

    logger.info("Analytics service shutting down")


app = FastAPI(
    title="Analytics Service",
    description="Tracks URL access statistics for the URL shortener",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(stats_router)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint for load balancers and Docker health checks."""
    return {"status": "healthy"}


@app.exception_handler(InvalidLimitError)
async def invalid_limit_error_handler(
    request: Request, exc: InvalidLimitError
) -> JSONResponse:
    """Map InvalidLimitError to HTTP 400 Bad Request."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

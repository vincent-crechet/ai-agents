"""
FastAPI application entry point for the url-management service.

Configures the application with routes, exception handlers, and
lifespan management for the message broker connection.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.urls import router
from app.dependencies import broker, engine
from app.exceptions.url_exceptions import InvalidUrlError, UrlNotFoundError
from app.models.url_mapping import Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan: connect/disconnect message broker."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    try:
        await broker.connect()
        logger.info("Application started, broker connected")
    except Exception as e:
        logger.warning("Failed to connect to broker on startup", extra={"error": str(e)})
    yield
    try:
        await broker.close()
        logger.info("Application shutdown, broker disconnected")
    except Exception as e:
        logger.warning("Error closing broker connection", extra={"error": str(e)})


app = FastAPI(
    title="URL Management Service",
    description="Service for shortening and resolving URLs",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for load balancers and Docker health checks."""
    return {"status": "healthy"}


app.include_router(router)


@app.exception_handler(UrlNotFoundError)
async def url_not_found_handler(request: Request, exc: UrlNotFoundError) -> JSONResponse:
    """Map UrlNotFoundError to 404 Not Found."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidUrlError)
async def invalid_url_handler(request: Request, exc: InvalidUrlError) -> JSONResponse:
    """Map InvalidUrlError to 400 Bad Request."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

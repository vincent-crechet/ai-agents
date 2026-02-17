"""
HTTP endpoints for URL management.

Provides the REST API for shortening and resolving URLs.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, RedirectResponse

from architecture.contracts.url_management_service import (
    ShortenUrlRequest,
    ShortenUrlResponse,
)

from app.dependencies import get_url_service
from app.services.url_service import UrlManagementService

router = APIRouter()


@router.post("/api/v1/urls")
async def shorten_url(
    request: ShortenUrlRequest,
    service: UrlManagementService = Depends(get_url_service),
) -> JSONResponse:
    """
    Shorten a long URL.

    Returns 201 Created for new mappings, 200 OK for existing ones (idempotent).
    """
    # Check if this URL already exists to determine status code
    existing = await service._repository.find_by_long_url(request.long_url)
    result = await service.shorten_url(request)

    status_code = 200 if existing else 201
    return JSONResponse(
        content=result.model_dump(mode="json"),
        status_code=status_code,
    )


@router.get("/{short_code}")
async def redirect_url(
    short_code: str,
    service: UrlManagementService = Depends(get_url_service),
) -> RedirectResponse:
    """
    Resolve a short code and redirect to the original URL.

    Returns 301 Moved Permanently redirect.
    """
    result = await service.resolve_url(short_code)
    return RedirectResponse(url=result.long_url, status_code=301)

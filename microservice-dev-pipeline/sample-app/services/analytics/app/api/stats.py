"""
Stats API endpoints for the analytics service.

Exposes URL access statistics via RESTful endpoints.
"""

from fastapi import APIRouter, Depends, Query

from architecture.contracts.analytics_service import TopUrlsResponse
from app.dependencies import get_analytics_service
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/top", response_model=TopUrlsResponse)
async def get_top_urls(
    limit: int = Query(default=10),
    service: AnalyticsService = Depends(get_analytics_service),
) -> TopUrlsResponse:
    """
    Return the most accessed URLs ranked by access count.

    Args:
        limit: Maximum number of results to return (default 10).
        service: Injected analytics service instance.

    Returns:
        TopUrlsResponse with ranked URL statistics.
    """
    return await service.get_top_urls(limit=limit)

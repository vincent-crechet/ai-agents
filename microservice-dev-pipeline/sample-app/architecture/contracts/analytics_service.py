"""
Service interface contract for the analytics service.

Defines the external API that analytics exposes: DTOs, ABC interface,
and event routing declarations.
"""

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel, Field

from architecture.contracts.common import UrlAccessedEvent


# --- Request/Response DTOs ---


class UrlAccessStatsResponse(BaseModel):
    """Statistics for a single URL."""

    short_code: str = Field(..., description="The short URL code")
    long_url: str = Field(..., description="The original long URL")
    access_count: int = Field(..., description="Number of times the URL was accessed")


class TopUrlsResponse(BaseModel):
    """Response containing the most accessed URLs."""

    urls: List[UrlAccessStatsResponse] = Field(
        ..., description="List of URLs ranked by access count descending"
    )


# --- Service Interface ABC ---


class IAnalyticsService(ABC):
    """Service interface defining the external API for analytics."""

    @abstractmethod
    async def get_top_urls(self, limit: int = 10) -> TopUrlsResponse:
        """
        Return the most accessed URLs ranked by access count.

        Endpoint: GET /api/v1/stats/top?limit=N
        HTTP Status: 200 OK
        """
        ...

    @abstractmethod
    async def handle_url_accessed(self, event: UrlAccessedEvent) -> None:
        """
        Process a UrlAccessedEvent: increment the access counter for the URL.

        Triggered by: UrlAccessedEvent from url-management (async, via message broker)
        """
        ...


# --- Event Routing Declarations ---

EVENTS_PUBLISHED = []
EVENTS_CONSUMED = [UrlAccessedEvent]

"""
Analytics service implementation.

Inherits from the IAnalyticsService ABC defined in architecture contracts.
Implements URL access tracking and statistics retrieval.
"""

import logging

from architecture.contracts.analytics_service import (
    IAnalyticsService,
    TopUrlsResponse,
    UrlAccessStatsResponse,
)
from architecture.contracts.common import UrlAccessedEvent
from app.exceptions.analytics_exceptions import InvalidLimitError
from app.ports.repository import IAnalyticsRepository

logger = logging.getLogger(__name__)


class AnalyticsService(IAnalyticsService):
    """Concrete implementation of IAnalyticsService using repository port."""

    def __init__(self, repository: IAnalyticsRepository):
        self._repository = repository

    async def get_top_urls(self, limit: int = 10) -> TopUrlsResponse:
        """
        Return the most accessed URLs ranked by access count.

        Args:
            limit: Maximum number of results to return. Must be positive.

        Returns:
            TopUrlsResponse with URLs ranked by access count descending.

        Raises:
            InvalidLimitError: If limit is not a positive integer.
        """
        if limit <= 0:
            raise InvalidLimitError(limit)

        stats_list = await self._repository.get_top_urls(limit)

        urls = [
            UrlAccessStatsResponse(
                short_code=stats.short_code,
                long_url=stats.long_url,
                access_count=stats.access_count,
            )
            for stats in stats_list
        ]

        return TopUrlsResponse(urls=urls)

    async def handle_url_accessed(self, event: UrlAccessedEvent) -> None:
        """
        Process a UrlAccessedEvent by incrementing the access counter.

        Increments the counter for the URL identified by the event's short_code.
        If the URL is not yet tracked, creates a new record with count=1.
        Commits the transaction to persist changes.

        Args:
            event: The URL accessed event containing short_code and long_url.
        """
        await self._repository.increment_access_count(
            short_code=event.short_code,
            long_url=event.long_url,
        )
        await self._repository.commit()
        logger.info(
            "Handled URL accessed event",
            extra={"short_code": event.short_code},
        )

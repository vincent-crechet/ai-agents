"""
Repository port for analytics data persistence.

Defines the abstract interface for accessing URL access statistics.
"""

from abc import ABC, abstractmethod
from typing import List

from app.models.url_access_stats import UrlAccessStats


class IAnalyticsRepository(ABC):
    """Abstract interface for analytics data persistence."""

    @abstractmethod
    async def increment_access_count(
        self, short_code: str, long_url: str
    ) -> UrlAccessStats:
        """
        Increment the access count for a URL.

        If the short_code does not exist, create a new record with count=1.
        If it exists, increment the existing count.

        Args:
            short_code: The short URL code.
            long_url: The original long URL.

        Returns:
            The updated or created UrlAccessStats record.
        """
        ...

    @abstractmethod
    async def get_top_urls(self, limit: int) -> List[UrlAccessStats]:
        """
        Return the most accessed URLs ranked by access count descending.

        Args:
            limit: Maximum number of results to return.

        Returns:
            List of UrlAccessStats ordered by access_count DESC.
        """
        ...

    @abstractmethod
    async def commit(self) -> None:
        """
        Commit the current transaction.

        Required for event handler persistence pattern.
        """
        ...

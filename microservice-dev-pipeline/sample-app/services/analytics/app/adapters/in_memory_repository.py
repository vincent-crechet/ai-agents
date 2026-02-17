"""
In-memory adapter for the analytics repository port.

Used for unit testing without database dependencies.
"""

from datetime import datetime, timezone
from typing import Dict, List

from app.models.url_access_stats import UrlAccessStats
from app.ports.repository import IAnalyticsRepository


class InMemoryAnalyticsRepository(IAnalyticsRepository):
    """In-memory implementation of the analytics repository for testing."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict] = {}
        self._id_counter: int = 0

    async def increment_access_count(
        self, short_code: str, long_url: str
    ) -> UrlAccessStats:
        """
        Increment access count for a URL in memory.

        Args:
            short_code: The short URL code.
            long_url: The original long URL.

        Returns:
            The updated or newly created UrlAccessStats record.
        """
        now = datetime.now(timezone.utc)

        if short_code in self._store:
            self._store[short_code]["access_count"] += 1
            self._store[short_code]["last_accessed_at"] = now
        else:
            self._id_counter += 1
            self._store[short_code] = {
                "id": self._id_counter,
                "short_code": short_code,
                "long_url": long_url,
                "access_count": 1,
                "last_accessed_at": now,
            }

        data = self._store[short_code]
        stats = UrlAccessStats()
        stats.id = data["id"]
        stats.short_code = data["short_code"]
        stats.long_url = data["long_url"]
        stats.access_count = data["access_count"]
        stats.last_accessed_at = data["last_accessed_at"]
        return stats

    async def get_top_urls(self, limit: int) -> List[UrlAccessStats]:
        """
        Return the most accessed URLs ordered by access count descending.

        Args:
            limit: Maximum number of results to return.

        Returns:
            List of UrlAccessStats ordered by access_count DESC.
        """
        sorted_items = sorted(
            self._store.values(),
            key=lambda item: item["access_count"],
            reverse=True,
        )

        results = []
        for data in sorted_items[:limit]:
            stats = UrlAccessStats()
            stats.id = data["id"]
            stats.short_code = data["short_code"]
            stats.long_url = data["long_url"]
            stats.access_count = data["access_count"]
            stats.last_accessed_at = data["last_accessed_at"]
            results.append(stats)

        return results

    async def commit(self) -> None:
        """No-op for in-memory repository."""
        pass

"""
Mock implementation of IAnalyticsService for use case testing.

Uses in-memory storage and subscribes to UrlAccessedEvent via MockEventBus.
"""

from typing import Dict

from architecture.contracts.common import UrlAccessedEvent
from architecture.contracts.analytics_service import (
    IAnalyticsService,
    UrlAccessStatsResponse,
    TopUrlsResponse,
)
from use_case_tests.harnesses.mock_event_bus import MockEventBus


class MockAnalyticsService(IAnalyticsService):
    """In-memory implementation of analytics service."""

    def __init__(self, event_bus: MockEventBus):
        self._event_bus = event_bus
        self._access_stats: Dict[str, Dict] = {}  # short_code -> {long_url, count}

        # Subscribe to events
        self._event_bus.subscribe(UrlAccessedEvent, self._handle_url_accessed_sync)

    def _handle_url_accessed_sync(self, event: UrlAccessedEvent):
        """Synchronous handler for MockEventBus dispatch."""
        if event.short_code in self._access_stats:
            self._access_stats[event.short_code]["access_count"] += 1
        else:
            self._access_stats[event.short_code] = {
                "long_url": event.long_url,
                "access_count": 1,
            }

    async def handle_url_accessed(self, event: UrlAccessedEvent) -> None:
        """Async interface method — in mock, already handled via event bus subscription."""
        self._handle_url_accessed_sync(event)

    async def get_top_urls(self, limit: int = 10) -> TopUrlsResponse:
        """Return the most accessed URLs ranked by access count descending."""
        sorted_stats = sorted(
            self._access_stats.items(),
            key=lambda item: item[1]["access_count"],
            reverse=True,
        )

        urls = [
            UrlAccessStatsResponse(
                short_code=short_code,
                long_url=data["long_url"],
                access_count=data["access_count"],
            )
            for short_code, data in sorted_stats[:limit]
        ]

        return TopUrlsResponse(urls=urls)

"""
MockTestHarness — composes all mock services with a shared event bus.

Implements the ITestHarness protocol for fast, in-memory use case validation.
"""

from typing import List

from pydantic import BaseModel

from architecture.contracts.url_management_service import ShortenUrlResponse
from architecture.contracts.analytics_service import TopUrlsResponse
from use_case_tests.harnesses.mock_event_bus import MockEventBus
from use_case_tests.harnesses.mock_url_management_service import MockUrlManagementService
from use_case_tests.harnesses.mock_analytics_service import MockAnalyticsService


class MockTestHarness:
    """Orchestrates mock services for use case testing."""

    def __init__(self):
        self._event_bus = MockEventBus()
        self._url_management = MockUrlManagementService(self._event_bus)
        self._analytics = MockAnalyticsService(self._event_bus)

    async def shorten_url(self, long_url: str) -> ShortenUrlResponse:
        """Shorten a long URL via url-management service."""
        from architecture.contracts.url_management_service import ShortenUrlRequest

        request = ShortenUrlRequest(long_url=long_url)
        return await self._url_management.shorten_url(request)

    async def resolve_url(self, short_code: str) -> str:
        """Resolve a short code to the original long URL."""
        response = await self._url_management.resolve_url(short_code)
        return response.long_url

    async def get_top_urls(self, limit: int = 10) -> TopUrlsResponse:
        """Get the most accessed URLs from analytics service."""
        return await self._analytics.get_top_urls(limit=limit)

    def get_published_events(self) -> List[BaseModel]:
        """Return all events published during the test."""
        return self._event_bus.get_published_events()

    async def wait_for_events_processed(self) -> None:
        """In mock implementation, events are processed synchronously. No-op."""
        pass

    def reset(self) -> None:
        """Reset all state for test isolation."""
        self._event_bus = MockEventBus()
        self._url_management = MockUrlManagementService(self._event_bus)
        self._analytics = MockAnalyticsService(self._event_bus)

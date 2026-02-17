"""
ITestHarness Protocol — simplified async API for tests to call across services.

Tests are written against this Protocol. Two implementations exist:
- MockTestHarness (activity 04): in-memory, for fast architect validation
- RealServiceHarness (activity 06): HTTP-based, for integration testing

Both implement the same Protocol so tests run unchanged against either.
"""

from typing import List, Protocol, runtime_checkable

from pydantic import BaseModel

from architecture.contracts.url_management_service import ShortenUrlResponse
from architecture.contracts.analytics_service import TopUrlsResponse


@runtime_checkable
class ITestHarness(Protocol):
    """Test harness protocol abstracting service orchestration."""

    async def shorten_url(self, long_url: str) -> ShortenUrlResponse:
        """Shorten a long URL. Delegates to url-management service."""
        ...

    async def resolve_url(self, short_code: str) -> str:
        """Resolve a short code to the original long URL. Returns the long URL string."""
        ...

    async def get_top_urls(self, limit: int = 10) -> TopUrlsResponse:
        """Get the most accessed URLs. Delegates to analytics service."""
        ...

    def get_published_events(self) -> List[BaseModel]:
        """Return all events published during the test."""
        ...

    async def wait_for_events_processed(self) -> None:
        """Wait until all published events have been processed by consumers."""
        ...

    def reset(self) -> None:
        """Reset all state for test isolation."""
        ...

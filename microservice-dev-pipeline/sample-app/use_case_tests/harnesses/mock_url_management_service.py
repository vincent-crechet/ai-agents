"""
Mock implementation of IUrlManagementService for use case testing.

Uses in-memory storage and publishes events via MockEventBus.
Implements deterministic short code generation (hash-based) to match
the idempotency requirement.
"""

import hashlib
from typing import Dict

from architecture.contracts.common import UrlAccessedEvent
from architecture.contracts.url_management_service import (
    IUrlManagementService,
    ShortenUrlRequest,
    ShortenUrlResponse,
    ResolveUrlResponse,
)
from use_case_tests.harnesses.mock_event_bus import MockEventBus


class UrlNotFoundError(Exception):
    """Raised when a short code does not exist."""

    def __init__(self, short_code: str):
        self.short_code = short_code
        super().__init__(f"Short URL not found: {short_code}")


class MockUrlManagementService(IUrlManagementService):
    """In-memory implementation of url-management service."""

    def __init__(self, event_bus: MockEventBus):
        self._event_bus = event_bus
        self._url_mappings: Dict[str, str] = {}  # short_code -> long_url
        self._reverse_mappings: Dict[str, str] = {}  # long_url -> short_code

    def _generate_short_code(self, long_url: str) -> str:
        """Generate a deterministic short code from a long URL."""
        return hashlib.sha256(long_url.encode()).hexdigest()[:8]

    async def shorten_url(self, request: ShortenUrlRequest) -> ShortenUrlResponse:
        """Shorten a URL. Same long URL always returns the same short code."""
        long_url = request.long_url

        # Return existing mapping if it exists
        if long_url in self._reverse_mappings:
            short_code = self._reverse_mappings[long_url]
        else:
            short_code = self._generate_short_code(long_url)
            self._url_mappings[short_code] = long_url
            self._reverse_mappings[long_url] = short_code

        return ShortenUrlResponse(
            short_code=short_code,
            short_url=f"http://short.url/{short_code}",
            long_url=long_url,
        )

    async def resolve_url(self, short_code: str) -> ResolveUrlResponse:
        """Resolve a short code to the original long URL and publish access event."""
        if short_code not in self._url_mappings:
            raise UrlNotFoundError(short_code)

        long_url = self._url_mappings[short_code]

        self._event_bus.publish(
            UrlAccessedEvent(short_code=short_code, long_url=long_url)
        )

        return ResolveUrlResponse(long_url=long_url)

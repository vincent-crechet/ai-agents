"""
In-memory repository adapter for URL mapping persistence.

Used in unit tests to avoid database dependencies. Stores URL mappings
in dictionaries for fast lookup by short code or long URL.
"""

from typing import Dict, Optional

from app.models.url_mapping import UrlMapping
from app.ports.repository import IUrlRepository


class InMemoryUrlRepository(IUrlRepository):
    """In-memory implementation of the URL repository port for testing."""

    def __init__(self) -> None:
        self._by_short_code: Dict[str, UrlMapping] = {}
        self._by_long_url: Dict[str, UrlMapping] = {}
        self._id_counter: int = 0

    async def save(self, url_mapping: UrlMapping) -> UrlMapping:
        """Store a URL mapping in memory."""
        self._id_counter += 1
        url_mapping.id = self._id_counter
        self._by_short_code[url_mapping.short_code] = url_mapping
        self._by_long_url[url_mapping.long_url] = url_mapping
        return url_mapping

    async def find_by_short_code(self, short_code: str) -> Optional[UrlMapping]:
        """Look up a URL mapping by short code in memory."""
        return self._by_short_code.get(short_code)

    async def find_by_long_url(self, long_url: str) -> Optional[UrlMapping]:
        """Look up a URL mapping by long URL in memory."""
        return self._by_long_url.get(long_url)

    async def commit(self) -> None:
        """No-op for in-memory repository."""
        pass

"""
Repository port for URL mapping persistence.

Defines the abstract interface for storing and retrieving URL mappings.
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.models.url_mapping import UrlMapping


class IUrlRepository(ABC):
    """Abstract interface for URL mapping persistence."""

    @abstractmethod
    async def save(self, url_mapping: UrlMapping) -> UrlMapping:
        """
        Persist a URL mapping.

        Args:
            url_mapping: The URL mapping to save.

        Returns:
            The persisted URL mapping.
        """
        ...

    @abstractmethod
    async def find_by_short_code(self, short_code: str) -> Optional[UrlMapping]:
        """
        Find a URL mapping by its short code.

        Args:
            short_code: The short code to look up.

        Returns:
            The URL mapping if found, None otherwise.
        """
        ...

    @abstractmethod
    async def find_by_long_url(self, long_url: str) -> Optional[UrlMapping]:
        """
        Find a URL mapping by its long URL.

        Args:
            long_url: The long URL to look up.

        Returns:
            The URL mapping if found, None otherwise.
        """
        ...

    @abstractmethod
    async def commit(self) -> None:
        """
        Commit the current transaction.

        Used by event handlers to persist changes.
        """
        ...

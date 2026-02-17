"""
Core business logic for URL management.

Implements the IUrlManagementService contract with deterministic
short code generation and event publishing on URL resolution.
"""

import hashlib
import logging
import re
from datetime import datetime, timezone

from architecture.contracts.common import UrlAccessedEvent
from architecture.contracts.url_management_service import (
    IUrlManagementService,
    ResolveUrlResponse,
    ShortenUrlRequest,
    ShortenUrlResponse,
)

from app.exceptions.url_exceptions import InvalidUrlError, UrlNotFoundError
from app.models.url_mapping import UrlMapping
from app.ports.message_broker import IMessageBroker
from app.ports.repository import IUrlRepository

logger = logging.getLogger(__name__)

# Simple URL pattern: must have a scheme (http/https) and a host
URL_PATTERN = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)


class UrlManagementService(IUrlManagementService):
    """
    Concrete implementation of the URL management service.

    Provides deterministic URL shortening via SHA-256 hashing and
    publishes UrlAccessedEvent on each URL resolution.
    """

    def __init__(
        self,
        repository: IUrlRepository,
        message_broker: IMessageBroker,
        base_url: str,
    ):
        self._repository = repository
        self._message_broker = message_broker
        self._base_url = base_url.rstrip("/")

    @staticmethod
    def _generate_short_code(long_url: str) -> str:
        """Generate a deterministic short code from a long URL using SHA-256."""
        return hashlib.sha256(long_url.encode()).hexdigest()[:8]

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate that the given string is a valid HTTP(S) URL."""
        if not url or not url.strip():
            raise InvalidUrlError(url, "URL must not be empty")
        if not URL_PATTERN.match(url):
            raise InvalidUrlError(url, "URL must start with http:// or https:// and be well-formed")

    async def shorten_url(self, request: ShortenUrlRequest) -> ShortenUrlResponse:
        """
        Create a short URL for the given long URL.

        Idempotent: the same long URL always returns the same short URL.
        Returns the existing mapping if one already exists.
        """
        self._validate_url(request.long_url)

        # Check if this URL has already been shortened
        existing = await self._repository.find_by_long_url(request.long_url)
        if existing:
            logger.info(
                "Returning existing short URL",
                extra={"short_code": existing.short_code, "long_url": request.long_url},
            )
            return ShortenUrlResponse(
                short_code=existing.short_code,
                short_url=f"{self._base_url}/{existing.short_code}",
                long_url=request.long_url,
            )

        # Generate deterministic short code and persist
        short_code = self._generate_short_code(request.long_url)
        url_mapping = UrlMapping(
            short_code=short_code,
            long_url=request.long_url,
            created_at=datetime.now(timezone.utc),
        )
        await self._repository.save(url_mapping)
        await self._repository.commit()

        logger.info(
            "Created new short URL",
            extra={"short_code": short_code, "long_url": request.long_url},
        )

        return ShortenUrlResponse(
            short_code=short_code,
            short_url=f"{self._base_url}/{short_code}",
            long_url=request.long_url,
        )

    async def resolve_url(self, short_code: str) -> ResolveUrlResponse:
        """
        Resolve a short code to the original long URL.

        Publishes a UrlAccessedEvent on successful resolution.
        Raises UrlNotFoundError if the short code does not exist.
        """
        url_mapping = await self._repository.find_by_short_code(short_code)
        if url_mapping is None:
            raise UrlNotFoundError(short_code)

        # Publish access event
        event = UrlAccessedEvent(
            short_code=short_code,
            long_url=url_mapping.long_url,
            accessed_at=datetime.now(timezone.utc),
        )
        await self._message_broker.publish(event, routing_key="url.accessed")

        logger.info(
            "Resolved short URL",
            extra={"short_code": short_code, "long_url": url_mapping.long_url},
        )

        return ResolveUrlResponse(long_url=url_mapping.long_url)

"""
Service interface contract for the url-management service.

Defines the external API that url-management exposes: DTOs, ABC interface,
and event routing declarations.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from architecture.contracts.common import UrlAccessedEvent


# --- Request/Response DTOs ---


class ShortenUrlRequest(BaseModel):
    """Request to shorten a long URL."""

    long_url: str = Field(..., description="The original long URL to shorten")


class ShortenUrlResponse(BaseModel):
    """Response containing the shortened URL."""

    short_code: str = Field(..., description="The generated short URL code")
    short_url: str = Field(..., description="The full short URL")
    long_url: str = Field(..., description="The original long URL")


class ResolveUrlResponse(BaseModel):
    """Response containing the resolved long URL."""

    long_url: str = Field(..., description="The original long URL to redirect to")


# --- Service Interface ABC ---


class IUrlManagementService(ABC):
    """Service interface defining the external API for url-management."""

    @abstractmethod
    async def shorten_url(self, request: ShortenUrlRequest) -> ShortenUrlResponse:
        """
        Create a short URL for the given long URL. Idempotent: the same long URL
        always returns the same short URL.

        Endpoint: POST /api/v1/urls
        HTTP Status: 201 Created
        """
        ...

    @abstractmethod
    async def resolve_url(self, short_code: str) -> ResolveUrlResponse:
        """
        Resolve a short code to the original long URL.

        Endpoint: GET /{short_code}
        HTTP Status: 301 Moved Permanently (redirect)
        Raises: UrlNotFoundError if short_code does not exist
        """
        ...


# --- Event Routing Declarations ---

EVENTS_PUBLISHED = [UrlAccessedEvent]
EVENTS_CONSUMED = []

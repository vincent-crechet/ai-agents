"""
Unit tests for UrlManagementService.

Uses in-memory adapters to test business logic without external dependencies.
"""

import pytest

from architecture.contracts.common import UrlAccessedEvent
from architecture.contracts.url_management_service import ShortenUrlRequest

from app.adapters.in_memory_broker import InMemoryBroker
from app.adapters.in_memory_repository import InMemoryUrlRepository
from app.exceptions.url_exceptions import InvalidUrlError, UrlNotFoundError
from app.services.url_service import UrlManagementService


@pytest.fixture
def repository() -> InMemoryUrlRepository:
    """Provide a fresh in-memory repository for each test."""
    return InMemoryUrlRepository()


@pytest.fixture
def broker() -> InMemoryBroker:
    """Provide a fresh in-memory broker for each test."""
    return InMemoryBroker()


@pytest.fixture
def service(repository: InMemoryUrlRepository, broker: InMemoryBroker) -> UrlManagementService:
    """Provide a fully wired service using in-memory adapters."""
    return UrlManagementService(
        repository=repository,
        message_broker=broker,
        base_url="http://short.url",
    )


@pytest.mark.asyncio
async def test_shorten_valid_url(service: UrlManagementService) -> None:
    """Test that a valid URL is shortened successfully."""
    request = ShortenUrlRequest(long_url="https://example.com/very/long/path")
    result = await service.shorten_url(request)

    assert result.long_url == "https://example.com/very/long/path"
    assert result.short_code is not None
    assert len(result.short_code) == 8
    assert result.short_url == f"http://short.url/{result.short_code}"


@pytest.mark.asyncio
async def test_shorten_url_idempotency(service: UrlManagementService) -> None:
    """Test that shortening the same URL twice returns the same short code."""
    request = ShortenUrlRequest(long_url="https://example.com/idempotent")

    result1 = await service.shorten_url(request)
    result2 = await service.shorten_url(request)

    assert result1.short_code == result2.short_code
    assert result1.short_url == result2.short_url
    assert result1.long_url == result2.long_url


@pytest.mark.asyncio
async def test_resolve_valid_short_code(service: UrlManagementService) -> None:
    """Test that a valid short code resolves to the original URL."""
    request = ShortenUrlRequest(long_url="https://example.com/resolve-test")
    shorten_result = await service.shorten_url(request)

    resolve_result = await service.resolve_url(shorten_result.short_code)

    assert resolve_result.long_url == "https://example.com/resolve-test"


@pytest.mark.asyncio
async def test_resolve_not_found(service: UrlManagementService) -> None:
    """Test that resolving a non-existent short code raises UrlNotFoundError."""
    with pytest.raises(UrlNotFoundError) as exc_info:
        await service.resolve_url("nonexist")

    assert "nonexist" in str(exc_info.value)


@pytest.mark.asyncio
async def test_event_published_on_resolve(
    service: UrlManagementService,
    broker: InMemoryBroker,
) -> None:
    """Test that a UrlAccessedEvent is published when a URL is resolved."""
    request = ShortenUrlRequest(long_url="https://example.com/event-test")
    shorten_result = await service.shorten_url(request)

    await service.resolve_url(shorten_result.short_code)

    assert len(broker.published_events) == 1
    event, routing_key = broker.published_events[0]
    assert isinstance(event, UrlAccessedEvent)
    assert event.short_code == shorten_result.short_code
    assert event.long_url == "https://example.com/event-test"
    assert routing_key == "url.accessed"


@pytest.mark.asyncio
async def test_invalid_url_raises_error(service: UrlManagementService) -> None:
    """Test that an invalid URL raises InvalidUrlError."""
    with pytest.raises(InvalidUrlError):
        await service.shorten_url(ShortenUrlRequest(long_url="not-a-valid-url"))


@pytest.mark.asyncio
async def test_empty_url_raises_error(service: UrlManagementService) -> None:
    """Test that an empty URL raises InvalidUrlError."""
    with pytest.raises(InvalidUrlError):
        await service.shorten_url(ShortenUrlRequest(long_url=""))


@pytest.mark.asyncio
async def test_different_urls_produce_different_codes(service: UrlManagementService) -> None:
    """Test that different URLs produce different short codes."""
    result1 = await service.shorten_url(ShortenUrlRequest(long_url="https://example.com/one"))
    result2 = await service.shorten_url(ShortenUrlRequest(long_url="https://example.com/two"))

    assert result1.short_code != result2.short_code

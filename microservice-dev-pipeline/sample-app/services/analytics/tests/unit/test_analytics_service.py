"""
Unit tests for the AnalyticsService.

Uses InMemoryAnalyticsRepository to test business logic without database.
"""

import pytest
from datetime import datetime, timezone

from architecture.contracts.common import UrlAccessedEvent
from app.adapters.in_memory_repository import InMemoryAnalyticsRepository
from app.exceptions.analytics_exceptions import InvalidLimitError
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def repository() -> InMemoryAnalyticsRepository:
    """Provide a fresh in-memory repository for each test."""
    return InMemoryAnalyticsRepository()


@pytest.fixture
def service(repository: InMemoryAnalyticsRepository) -> AnalyticsService:
    """Provide a service instance with in-memory repository."""
    return AnalyticsService(repository=repository)


def _make_event(
    short_code: str = "abc123",
    long_url: str = "https://example.com",
) -> UrlAccessedEvent:
    """Helper to create a UrlAccessedEvent."""
    return UrlAccessedEvent(
        short_code=short_code,
        long_url=long_url,
        accessed_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_handle_event_increments_count(service: AnalyticsService) -> None:
    """Handling a URL accessed event should increment the access count."""
    event = _make_event(short_code="abc123", long_url="https://example.com")
    await service.handle_url_accessed(event)

    result = await service.get_top_urls(limit=10)
    assert len(result.urls) == 1
    assert result.urls[0].short_code == "abc123"
    assert result.urls[0].access_count == 1


@pytest.mark.asyncio
async def test_handle_event_new_url_creates_record(
    service: AnalyticsService,
) -> None:
    """Handling an event for a new URL should create a new record with count=1."""
    event = _make_event(short_code="new123", long_url="https://new.example.com")
    await service.handle_url_accessed(event)

    result = await service.get_top_urls(limit=10)
    assert len(result.urls) == 1
    assert result.urls[0].short_code == "new123"
    assert result.urls[0].long_url == "https://new.example.com"
    assert result.urls[0].access_count == 1


@pytest.mark.asyncio
async def test_get_top_urls_returns_ranked(service: AnalyticsService) -> None:
    """Top URLs should be returned ranked by access count descending."""
    # Create URL A with 3 accesses
    for _ in range(3):
        await service.handle_url_accessed(
            _make_event(short_code="aaa", long_url="https://a.com")
        )

    # Create URL B with 1 access
    await service.handle_url_accessed(
        _make_event(short_code="bbb", long_url="https://b.com")
    )

    # Create URL C with 2 accesses
    for _ in range(2):
        await service.handle_url_accessed(
            _make_event(short_code="ccc", long_url="https://c.com")
        )

    result = await service.get_top_urls(limit=10)
    assert len(result.urls) == 3
    assert result.urls[0].short_code == "aaa"
    assert result.urls[0].access_count == 3
    assert result.urls[1].short_code == "ccc"
    assert result.urls[1].access_count == 2
    assert result.urls[2].short_code == "bbb"
    assert result.urls[2].access_count == 1


@pytest.mark.asyncio
async def test_get_top_urls_with_limit(service: AnalyticsService) -> None:
    """Top URLs should respect the limit parameter."""
    for code in ["aaa", "bbb", "ccc", "ddd"]:
        await service.handle_url_accessed(
            _make_event(short_code=code, long_url=f"https://{code}.com")
        )

    result = await service.get_top_urls(limit=2)
    assert len(result.urls) == 2


@pytest.mark.asyncio
async def test_get_top_urls_empty(service: AnalyticsService) -> None:
    """Top URLs should return an empty list when no URLs have been accessed."""
    result = await service.get_top_urls(limit=10)
    assert len(result.urls) == 0
    assert result.urls == []


@pytest.mark.asyncio
async def test_handle_multiple_events_same_url(
    service: AnalyticsService,
) -> None:
    """Multiple events for the same URL should increment the counter each time."""
    event = _make_event(short_code="repeat", long_url="https://repeat.com")

    for _ in range(5):
        await service.handle_url_accessed(event)

    result = await service.get_top_urls(limit=10)
    assert len(result.urls) == 1
    assert result.urls[0].short_code == "repeat"
    assert result.urls[0].access_count == 5


@pytest.mark.asyncio
async def test_get_top_urls_invalid_limit(service: AnalyticsService) -> None:
    """Requesting top URLs with a non-positive limit should raise InvalidLimitError."""
    with pytest.raises(InvalidLimitError):
        await service.get_top_urls(limit=0)

    with pytest.raises(InvalidLimitError):
        await service.get_top_urls(limit=-1)

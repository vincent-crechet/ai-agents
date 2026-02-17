"""
Tests for UC-002: Redirect via Short URL

Validates acceptance criteria:
- Given a valid short URL, the user is redirected to the original long URL
- Given a short URL that does not exist, the user sees an error
- Validates UrlAccessedEvent is published on redirect
"""

import pytest

from architecture.contracts.common import UrlAccessedEvent
from use_case_tests.harnesses.mock_url_management_service import UrlNotFoundError


@pytest.mark.asyncio
async def test_resolve_valid_short_url(test_harness):
    """Given a valid short URL, when accessed, then the user is redirected to the original."""
    long_url = "https://www.example.com/original"
    shorten_result = await test_harness.shorten_url(long_url)

    resolved_url = await test_harness.resolve_url(shorten_result.short_code)

    assert resolved_url == long_url


@pytest.mark.asyncio
async def test_resolve_nonexistent_short_url(test_harness):
    """Given a short URL that does not exist, when accessed, then an error is raised."""
    with pytest.raises(UrlNotFoundError):
        await test_harness.resolve_url("nonexistent")


@pytest.mark.asyncio
async def test_resolve_publishes_url_accessed_event(test_harness):
    """Given a successful redirect, then a UrlAccessedEvent is published."""
    long_url = "https://www.example.com/tracked"
    shorten_result = await test_harness.shorten_url(long_url)

    await test_harness.resolve_url(shorten_result.short_code)
    await test_harness.wait_for_events_processed()

    events = test_harness.get_published_events()
    assert len(events) == 1
    assert isinstance(events[0], UrlAccessedEvent)
    assert events[0].short_code == shorten_result.short_code
    assert events[0].long_url == long_url

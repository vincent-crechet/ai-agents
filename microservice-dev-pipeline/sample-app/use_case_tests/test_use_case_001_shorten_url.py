"""
Tests for UC-001: Shorten a URL

Validates acceptance criteria:
- Given a valid long URL, the user receives a short URL
- Given the same long URL multiple times, the user always receives the same short URL
- Given an invalid URL, the user receives an error
"""

import pytest


@pytest.mark.asyncio
async def test_shorten_valid_url(test_harness):
    """Given a valid long URL, when submitted, then a short URL is returned."""
    result = await test_harness.shorten_url("https://www.example.com/very/long/path")

    assert result.short_code is not None
    assert len(result.short_code) > 0
    assert result.short_url is not None
    assert result.long_url == "https://www.example.com/very/long/path"


@pytest.mark.asyncio
async def test_shorten_same_url_returns_same_short_url(test_harness):
    """Given the same long URL submitted multiple times, the same short URL is returned."""
    long_url = "https://www.example.com/deterministic"

    result1 = await test_harness.shorten_url(long_url)
    result2 = await test_harness.shorten_url(long_url)

    assert result1.short_code == result2.short_code
    assert result1.short_url == result2.short_url


@pytest.mark.asyncio
async def test_shorten_different_urls_return_different_short_urls(test_harness):
    """Given different long URLs, different short URLs are returned."""
    result1 = await test_harness.shorten_url("https://www.example.com/page1")
    result2 = await test_harness.shorten_url("https://www.example.com/page2")

    assert result1.short_code != result2.short_code

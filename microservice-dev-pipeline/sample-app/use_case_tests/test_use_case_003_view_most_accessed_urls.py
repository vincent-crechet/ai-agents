"""
Tests for UC-003: View Most Accessed URLs

Validates acceptance criteria:
- Given URLs that have been accessed, the user sees a ranked list with access counts
- Given no URLs have been accessed, the user sees an empty list
- Validates end-to-end flow: shorten -> resolve -> view stats
"""

import pytest


@pytest.mark.asyncio
async def test_view_most_accessed_urls(test_harness):
    """Given URLs that have been accessed, when stats are viewed, then a ranked list is returned."""
    # Shorten two URLs
    result1 = await test_harness.shorten_url("https://www.example.com/popular")
    result2 = await test_harness.shorten_url("https://www.example.com/less-popular")

    # Access the first URL 3 times, second URL 1 time
    for _ in range(3):
        await test_harness.resolve_url(result1.short_code)
    await test_harness.resolve_url(result2.short_code)
    await test_harness.wait_for_events_processed()

    # View stats
    stats = await test_harness.get_top_urls()

    assert len(stats.urls) == 2
    assert stats.urls[0].short_code == result1.short_code
    assert stats.urls[0].long_url == "https://www.example.com/popular"
    assert stats.urls[0].access_count == 3
    assert stats.urls[1].short_code == result2.short_code
    assert stats.urls[1].long_url == "https://www.example.com/less-popular"
    assert stats.urls[1].access_count == 1


@pytest.mark.asyncio
async def test_view_stats_with_no_accesses(test_harness):
    """Given no URLs have been accessed, when stats are viewed, then an empty list is returned."""
    stats = await test_harness.get_top_urls()

    assert len(stats.urls) == 0


@pytest.mark.asyncio
async def test_view_stats_respects_limit(test_harness):
    """Given a limit parameter, when stats are viewed, then at most that many entries are returned."""
    # Create and access 3 different URLs
    for i in range(3):
        result = await test_harness.shorten_url(f"https://www.example.com/page{i}")
        await test_harness.resolve_url(result.short_code)
    await test_harness.wait_for_events_processed()

    stats = await test_harness.get_top_urls(limit=2)

    assert len(stats.urls) == 2


@pytest.mark.asyncio
async def test_stats_show_short_code_long_url_and_count(test_harness):
    """Given accessed URLs, each stat entry shows short code, original long URL, and access count."""
    long_url = "https://www.example.com/complete-info"
    result = await test_harness.shorten_url(long_url)
    await test_harness.resolve_url(result.short_code)
    await test_harness.wait_for_events_processed()

    stats = await test_harness.get_top_urls()

    assert len(stats.urls) == 1
    entry = stats.urls[0]
    assert entry.short_code == result.short_code
    assert entry.long_url == long_url
    assert entry.access_count == 1

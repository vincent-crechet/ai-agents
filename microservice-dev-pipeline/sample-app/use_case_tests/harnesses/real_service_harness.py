"""
RealServiceHarness — ITestHarness implementation using HTTP requests to real services.

Runs tests against containerized services deployed via Docker Compose.
"""

import logging
import time
from typing import List

import httpx
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from architecture.contracts.common import UrlAccessedEvent
from architecture.contracts.url_management_service import ShortenUrlResponse
from architecture.contracts.analytics_service import TopUrlsResponse, UrlAccessStatsResponse
from use_case_tests.harnesses.mock_url_management_service import UrlNotFoundError

logger = logging.getLogger(__name__)


class RealServiceHarness:
    """Test harness that delegates to real services via HTTP."""

    def __init__(
        self,
        url_management_url: str,
        analytics_url: str,
        url_management_db_url: str,
        analytics_db_url: str,
        rabbitmq_management_url: str,
    ):
        self._url_management_url = url_management_url
        self._analytics_url = analytics_url
        self._url_management_db_url = url_management_db_url
        self._analytics_db_url = analytics_db_url
        self._rabbitmq_management_url = rabbitmq_management_url
        self.client = httpx.Client(timeout=30.0, follow_redirects=False)
        self._published_events: List[BaseModel] = []

    async def shorten_url(self, long_url: str) -> ShortenUrlResponse:
        """Shorten a long URL via the url-management service API."""
        response = self.client.post(
            f"{self._url_management_url}/api/v1/urls",
            json={"long_url": long_url},
        )
        if response.status_code == 400:
            raise ValueError(response.json().get("detail", "Invalid URL"))
        response.raise_for_status()
        return ShortenUrlResponse(**response.json())

    async def resolve_url(self, short_code: str) -> str:
        """Resolve a short code via the url-management service API."""
        response = self.client.get(
            f"{self._url_management_url}/{short_code}",
        )
        if response.status_code == 404:
            raise UrlNotFoundError(short_code)
        if response.status_code == 301:
            return response.headers["location"]
        response.raise_for_status()
        return response.headers.get("location", "")

    async def get_top_urls(self, limit: int = 10) -> TopUrlsResponse:
        """Get the most accessed URLs from the analytics service API."""
        response = self.client.get(
            f"{self._analytics_url}/api/v1/stats/top",
            params={"limit": limit},
        )
        response.raise_for_status()
        return TopUrlsResponse(**response.json())

    def get_published_events(self) -> List[BaseModel]:
        """Query analytics DB directly to find processed events."""
        engine = create_engine(self._analytics_db_url, poolclass=NullPool)
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT short_code, long_url FROM url_access_stats")
                )
                events = []
                for row in result:
                    events.append(
                        UrlAccessedEvent(
                            short_code=row[0],
                            long_url=row[1],
                        )
                    )
                return events
        finally:
            engine.dispose()

    async def wait_for_events_processed(self, timeout: float = 10.0) -> None:
        """Poll the analytics database until events have been processed."""
        engine = create_engine(self._analytics_db_url, poolclass=NullPool)
        start = time.time()
        last_count = 0
        try:
            while time.time() - start < timeout:
                with engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT COUNT(*) FROM url_access_stats")
                    )
                    count = result.scalar()
                    if count is not None and count > last_count:
                        last_count = count
                        # Give a brief moment for any further events
                        time.sleep(0.5)
                        return
                time.sleep(0.3)
        finally:
            engine.dispose()

    def reset(self) -> None:
        """Reset all state for test isolation."""
        # Clear url-management database
        engine_um = create_engine(self._url_management_db_url, poolclass=NullPool)
        try:
            with engine_um.connect() as conn:
                conn.execute(text("DELETE FROM url_mappings"))
                conn.commit()
        finally:
            engine_um.dispose()

        # Clear analytics database
        engine_an = create_engine(self._analytics_db_url, poolclass=NullPool)
        try:
            with engine_an.connect() as conn:
                conn.execute(text("DELETE FROM url_access_stats"))
                conn.commit()
        finally:
            engine_an.dispose()

        # Purge RabbitMQ queues
        try:
            purge_response = httpx.delete(
                f"{self._rabbitmq_management_url}/api/queues/%2f/analytics.UrlAccessedEvent/contents",
                auth=("guest", "guest"),
                timeout=5.0,
            )
            logger.debug("RabbitMQ queue purge status: %s", purge_response.status_code)
        except Exception as e:
            logger.debug("Could not purge RabbitMQ queue: %s", e)

        self._published_events.clear()

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

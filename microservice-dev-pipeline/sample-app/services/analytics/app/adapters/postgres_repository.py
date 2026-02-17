"""
PostgreSQL adapter for the analytics repository port.

Uses SQLAlchemy async sessions for database access.
"""

import logging
from datetime import datetime, timezone
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url_access_stats import UrlAccessStats
from app.ports.repository import IAnalyticsRepository

logger = logging.getLogger(__name__)


class PostgresAnalyticsRepository(IAnalyticsRepository):
    """PostgreSQL implementation of the analytics repository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def increment_access_count(
        self, short_code: str, long_url: str
    ) -> UrlAccessStats:
        """
        Increment access count for a URL, creating a new record if it does not exist.

        Args:
            short_code: The short URL code.
            long_url: The original long URL.

        Returns:
            The updated or newly created UrlAccessStats record.
        """
        stmt = select(UrlAccessStats).where(
            UrlAccessStats.short_code == short_code
        )
        result = await self._session.execute(stmt)
        stats = result.scalar_one_or_none()

        if stats is not None:
            stats.access_count += 1
            stats.last_accessed_at = datetime.now(timezone.utc)
            logger.info(
                "Incremented access count",
                extra={
                    "short_code": short_code,
                    "new_count": stats.access_count,
                },
            )
        else:
            stats = UrlAccessStats(
                short_code=short_code,
                long_url=long_url,
                access_count=1,
                last_accessed_at=datetime.now(timezone.utc),
            )
            self._session.add(stats)
            logger.info(
                "Created new access stats record",
                extra={"short_code": short_code},
            )

        return stats

    async def get_top_urls(self, limit: int) -> List[UrlAccessStats]:
        """
        Return the most accessed URLs ordered by access count descending.

        Args:
            limit: Maximum number of results to return.

        Returns:
            List of UrlAccessStats ordered by access_count DESC.
        """
        stmt = (
            select(UrlAccessStats)
            .order_by(UrlAccessStats.access_count.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def commit(self) -> None:
        """Commit the current transaction to persist changes."""
        await self._session.commit()

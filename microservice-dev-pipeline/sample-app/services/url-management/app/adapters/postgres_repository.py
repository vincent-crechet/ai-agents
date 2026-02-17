"""
PostgreSQL repository adapter for URL mapping persistence.

Implements the IUrlRepository port using SQLAlchemy async sessions
for production database access.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url_mapping import UrlMapping
from app.ports.repository import IUrlRepository


class PostgresUrlRepository(IUrlRepository):
    """PostgreSQL implementation of the URL repository port."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, url_mapping: UrlMapping) -> UrlMapping:
        """Persist a URL mapping to PostgreSQL."""
        self._session.add(url_mapping)
        await self._session.flush()
        return url_mapping

    async def find_by_short_code(self, short_code: str) -> Optional[UrlMapping]:
        """Find a URL mapping by short code in PostgreSQL."""
        stmt = select(UrlMapping).where(UrlMapping.short_code == short_code)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_long_url(self, long_url: str) -> Optional[UrlMapping]:
        """Find a URL mapping by long URL in PostgreSQL."""
        stmt = select(UrlMapping).where(UrlMapping.long_url == long_url)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def commit(self) -> None:
        """Commit the current database transaction."""
        await self._session.commit()

"""
SQLAlchemy model for URL access statistics.

Tracks access counts and metadata for shortened URLs.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


class UrlAccessStats(Base):
    """Stores access statistics for each shortened URL."""

    __tablename__ = "url_access_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    short_code = Column(String, unique=True, nullable=False, index=True)
    long_url = Column(String, nullable=False)
    access_count = Column(Integer, nullable=False, default=0)
    last_accessed_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
    )

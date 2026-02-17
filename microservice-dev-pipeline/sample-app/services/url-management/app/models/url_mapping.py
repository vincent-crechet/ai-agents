"""
SQLAlchemy model for URL mappings.

Defines the database schema for storing short code to long URL mappings.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Text, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class UrlMapping(Base):
    """Database model representing a mapping between a short code and a long URL."""

    __tablename__ = "url_mappings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    long_url: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<UrlMapping(id={self.id}, short_code='{self.short_code}')>"

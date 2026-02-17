"""
Shared event definitions used across services.

Events defined here are published by one service and consumed by another.
They represent the asynchronous communication contracts between services.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class UrlAccessedEvent(BaseModel):
    """
    Event published by url-management when a short URL is resolved and redirected.
    Consumed by analytics to track access counts.

    Publisher: url-management
    Consumer: analytics
    """

    short_code: str = Field(..., description="The short URL code that was accessed")
    long_url: str = Field(..., description="The original long URL that was resolved")
    accessed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the URL was accessed",
    )

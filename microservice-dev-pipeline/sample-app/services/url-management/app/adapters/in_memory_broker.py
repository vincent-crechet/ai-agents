"""
In-memory message broker adapter for testing.

Stores published events in a list for test assertions instead of
sending them to a real message broker.
"""

from typing import List, Tuple

from pydantic import BaseModel

from app.ports.message_broker import IMessageBroker


class InMemoryBroker(IMessageBroker):
    """In-memory implementation of the message broker port for testing."""

    def __init__(self) -> None:
        self.published_events: List[Tuple[BaseModel, str]] = []

    async def connect(self) -> None:
        """No-op for in-memory broker."""
        pass

    async def publish(self, event: BaseModel, routing_key: str) -> None:
        """Store the event for later test assertions."""
        self.published_events.append((event, routing_key))

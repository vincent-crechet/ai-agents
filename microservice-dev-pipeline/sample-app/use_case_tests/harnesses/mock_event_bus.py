"""
Simple in-memory pub/sub event bus for mock service communication.
"""

from collections import defaultdict
from typing import Callable, Dict, List, Type

from pydantic import BaseModel


class MockEventBus:
    """In-memory event bus that synchronously dispatches events to subscribers."""

    def __init__(self):
        self._subscribers: Dict[Type, List[Callable]] = defaultdict(list)
        self._published_events: List[BaseModel] = []

    def subscribe(self, event_type: Type[BaseModel], handler: Callable):
        """Register a handler for a specific event type."""
        self._subscribers[event_type].append(handler)

    def publish(self, event: BaseModel):
        """Publish an event: record it and dispatch to all subscribers."""
        self._published_events.append(event)
        for handler in self._subscribers[type(event)]:
            handler(event)

    def get_published_events(self) -> List[BaseModel]:
        """Return a copy of all published events."""
        return self._published_events.copy()

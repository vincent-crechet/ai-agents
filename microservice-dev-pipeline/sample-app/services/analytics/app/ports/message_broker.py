"""
Message broker port for event consumption.

Defines the abstract interface for subscribing to events.
"""

from abc import ABC, abstractmethod
from typing import Callable, Type

from pydantic import BaseModel


class IMessageBroker(ABC):
    """Abstract interface for message broker operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the message broker."""
        ...

    @abstractmethod
    async def subscribe(
        self, event_type: Type[BaseModel], handler: Callable
    ) -> None:
        """
        Subscribe to events of the given type.

        Args:
            event_type: The Pydantic model class for the event.
            handler: Async callable to invoke when an event is received.
        """
        ...

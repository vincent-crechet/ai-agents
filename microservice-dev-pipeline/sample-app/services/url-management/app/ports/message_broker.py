"""
Message broker port for event publishing.

Defines the abstract interface for publishing domain events.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class IMessageBroker(ABC):
    """Abstract interface for message broker operations."""

    @abstractmethod
    async def publish(self, event: BaseModel, routing_key: str) -> None:
        """
        Publish an event to the message broker.

        Args:
            event: The domain event to publish.
            routing_key: The routing key for message routing.
        """
        ...

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish connection to the message broker.

        Must be called before publishing events.
        """
        ...

"""
In-memory adapter for the message broker port.

Used for unit testing without RabbitMQ dependencies.
"""

from typing import Callable, Dict, List, Type

from pydantic import BaseModel

from app.ports.message_broker import IMessageBroker


class InMemoryBroker(IMessageBroker):
    """In-memory implementation of the message broker for testing."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable]] = {}

    async def connect(self) -> None:
        """No-op for in-memory broker."""
        pass

    async def subscribe(
        self, event_type: Type[BaseModel], handler: Callable
    ) -> None:
        """
        Register a handler for the given event type.

        Args:
            event_type: The Pydantic model class for the event.
            handler: Async callable to invoke when an event is dispatched.
        """
        event_name = event_type.__name__
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    async def dispatch(self, event: BaseModel) -> None:
        """
        Dispatch an event to all registered handlers.

        Args:
            event: The event instance to dispatch.
        """
        event_name = type(event).__name__
        handlers = self._handlers.get(event_name, [])
        for handler in handlers:
            await handler(event)

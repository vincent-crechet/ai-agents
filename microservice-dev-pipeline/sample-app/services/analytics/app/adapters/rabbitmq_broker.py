"""
RabbitMQ adapter for the message broker port.

Implements the consumer pattern for subscribing to events.
"""

import json
import logging
from typing import Callable, Type

import aio_pika
from pydantic import BaseModel

from app.ports.message_broker import IMessageBroker

logger = logging.getLogger(__name__)

# Map event class names to routing keys
ROUTING_KEY_MAP = {
    "UrlAccessedEvent": "url.accessed",
}


class RabbitMQBroker(IMessageBroker):
    """RabbitMQ implementation of the message broker for event consumption."""

    def __init__(
        self, rabbitmq_url: str, exchange_name: str, service_name: str
    ):
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name
        self.service_name = service_name
        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        logger.info(
            "Connected to RabbitMQ",
            extra={"exchange": self.exchange_name},
        )

    async def subscribe(
        self, event_type: Type[BaseModel], handler: Callable
    ) -> None:
        """
        Subscribe to events of the given type.

        Creates a durable queue bound to the exchange with the appropriate
        routing key, and starts consuming messages.

        Args:
            event_type: The Pydantic model class for the event.
            handler: Async callable to invoke when an event is received.
        """
        exchange = await self.channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

        queue_name = f"{self.service_name}.{event_type.__name__}"
        queue = await self.channel.declare_queue(queue_name, durable=True)

        routing_key = ROUTING_KEY_MAP.get(
            event_type.__name__, event_type.__name__
        )
        await queue.bind(exchange, routing_key=routing_key)

        async def on_message(message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                try:
                    event = event_type(**json.loads(message.body.decode()))
                    await handler(event)
                    logger.info(
                        "Processed event",
                        extra={
                            "event_type": event_type.__name__,
                            "queue": queue_name,
                        },
                    )
                except Exception as e:
                    logger.error(
                        f"Error processing event: {e}",
                        exc_info=True,
                        extra={
                            "event_type": event_type.__name__,
                            "queue": queue_name,
                        },
                    )

        await queue.consume(on_message)
        logger.info(
            "Subscribed to events",
            extra={
                "event_type": event_type.__name__,
                "routing_key": routing_key,
                "queue": queue_name,
            },
        )

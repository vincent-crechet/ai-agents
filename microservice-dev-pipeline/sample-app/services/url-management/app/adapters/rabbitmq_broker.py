"""
RabbitMQ message broker adapter.

Implements the IMessageBroker port using aio-pika for production
event publishing to RabbitMQ.
"""

import logging

import aio_pika
from pydantic import BaseModel

from app.ports.message_broker import IMessageBroker

logger = logging.getLogger(__name__)


class RabbitMQBroker(IMessageBroker):
    """RabbitMQ implementation of the message broker port."""

    def __init__(self, rabbitmq_url: str, exchange_name: str):
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ and declare the exchange."""
        self._connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        logger.info("Connected to RabbitMQ", extra={"exchange": self.exchange_name})

    async def publish(self, event: BaseModel, routing_key: str) -> None:
        """Publish an event to the RabbitMQ exchange."""
        if self._exchange is None:
            raise RuntimeError("Message broker is not connected. Call connect() first.")

        message = aio_pika.Message(
            body=event.model_dump_json().encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await self._exchange.publish(message, routing_key=routing_key)
        logger.info(
            "Event published",
            extra={"routing_key": routing_key, "event_type": type(event).__name__},
        )

    async def close(self) -> None:
        """Close the RabbitMQ connection."""
        if self._connection:
            await self._connection.close()
            logger.info("Disconnected from RabbitMQ")

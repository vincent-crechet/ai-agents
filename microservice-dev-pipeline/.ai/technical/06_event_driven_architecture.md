# Event-Driven Architecture

Event contract design principles and RabbitMQ messaging patterns.

---

## Event Contract Design Principles

### 1. Self-Containment

Events must contain all data consumers need — no synchronous calls to other services.

```python
# ✅ Self-contained — consumer has everything it needs
class ResourceAccessedEvent(BaseModel):
    resource_id: str
    resource_name: str        # Included so consumer doesn't need to fetch it
    accessed_at: datetime
    user_agent: Optional[str] = None

# ❌ Incomplete — forces consumer to call publisher service
class ResourceAccessedEvent(BaseModel):
    resource_id: str          # Consumer must call another service to get resource_name
    accessed_at: datetime
```

### 2. Immutability

Events are historical facts. Use `frozen=True`:

```python
class ResourceAccessedEvent(BaseModel):
    resource_id: str
    accessed_at: datetime
    model_config = ConfigDict(frozen=True)
```

### 3. Required vs Optional Fields

- **Required**: Core business data that is always available
- **Optional**: Enrichment data that may be missing (e.g., user_agent, ip_address)

Never make a field optional just to avoid fixing the publisher.

### 4. Explicit Naming

Field names must be unambiguous: `accessed_at` not `timestamp`, `long_url` not `url`.

### 5. Event Docstrings

Document publisher, consumer, and routing key in each event's docstring:

```python
class ResourceAccessedEvent(BaseModel):
    """
    Published by: <publisher-service>
    Consumed by: <consumer-service>
    Routing key: resource.accessed
    """
```

---

## Event Design Checklist

- [ ] Self-contained (no service calls needed by consumer)
- [ ] Immutable (`frozen=True`)
- [ ] Explicit field names
- [ ] Only business-optional fields marked Optional
- [ ] Timezone-aware datetimes (`datetime.now(timezone.utc)`)
- [ ] Routing key documented in docstring
- [ ] Field validation constraints specified with `Field()`

---

## Event Evolution

### Additive Changes (Preferred)

Add new fields as optional, then migrate to required:

1. Add field as `Optional` with default
2. Update publisher to include field
3. Verify all published events include field
4. Make field required in contract
5. Update consumers

### Breaking Changes

Create a new event version with a new routing key:

```python
class ResourceAccessedEventV2(BaseModel):
    resource_id: str
    resource_name: str  # New required field (breaking)
# Routing key: resource.accessed.v2
```

Publish both versions during migration. Remove old version after consumers migrate.

---

## RabbitMQ Configuration

### Exchange

All services MUST use the same exchange configuration. Define in centralized settings:

```python
# app/config.py
class Settings(BaseSettings):
    rabbitmq_url: str
    rabbitmq_exchange: str = "<project-exchange-name>"
```

- Type: `TOPIC` (supports wildcard routing)
- Durable: `True` (survives broker restarts)
- Inject exchange name from config — never hardcode in adapters

### Routing Keys

Pattern: `<domain>.<action>` (e.g., `resource.accessed`, `resource.created`)

**Critical:** Publishers and consumers must agree on routing keys. Consumers must map event class names to routing keys:

```python
# Consumer adapter
routing_key_map = {
    "ResourceAccessedEvent": "resource.accessed",
    "ResourceCreatedEvent": "resource.created",
}
routing_key = routing_key_map.get(event_type.__name__, event_type.__name__)
```

### Queue Naming

Convention: `<service-name>.<event-class-name>` (e.g., `consumer-service.ResourceAccessedEvent`)

### Message Durability

- Exchange: `durable=True`
- Queue: `durable=True`
- Message: `delivery_mode=DeliveryMode.PERSISTENT`

---

## Publisher Pattern

```python
class RabbitMQBroker(IMessageBroker):
    def __init__(self, rabbitmq_url: str, exchange_name: str):
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name

    async def connect(self) -> None:
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

    async def publish(self, event: BaseModel, routing_key: str) -> None:
        message = aio_pika.Message(
            body=event.model_dump_json().encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await self.exchange.publish(message, routing_key=routing_key)
```

Key points:
- Use `connect_robust()` for automatic reconnection
- Use `model_dump_json()` for Pydantic V2 serialization
- Always specify routing_key explicitly

---

## Consumer Pattern

```python
class RabbitMQBroker(IMessageBroker):
    def __init__(self, rabbitmq_url: str, exchange_name: str, service_name: str):
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name
        self.service_name = service_name

    async def subscribe(self, event_type: Type[BaseModel], handler: Callable) -> None:
        exchange = await self.channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await self.channel.declare_queue(
            f"{self.service_name}.{event_type.__name__}", durable=True
        )

        # Map event class name to routing key
        routing_key_map = {"ResourceAccessedEvent": "resource.accessed"}
        routing_key = routing_key_map.get(event_type.__name__, event_type.__name__)
        await queue.bind(exchange, routing_key=routing_key)

        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    event = event_type(**json.loads(message.body.decode()))
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error processing event: {e}", exc_info=True)

        await queue.consume(on_message)
```

Key points:
- Set `prefetch_count` to limit concurrent processing
- Use `message.process()` for automatic ack/nack
- Map event class names to routing keys (don't use class name as routing key)

---

## Common Pitfalls

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| Exchange name mismatch | Events published but never consumed (silent) | Use centralized config; never hardcode |
| Routing key mismatch | Queues created but empty | Add routing key mapping in consumer |
| Using `.dict()` instead of `.model_dump_json()` | TypeError on datetime fields | Use Pydantic V2 API |
| Non-durable config | Events/queues lost on broker restart | Set `durable=True` and `PERSISTENT` delivery |
| No error handling in consumer | Service crashes on malformed messages | Wrap handler in try/except |
| Incomplete events | Consumer calls publisher service (coupling) | Include all required data in event |
| Naive datetimes | Serialization issues | Use `datetime.now(timezone.utc)` |

---

## Configuration Checklist

- [ ] Exchange name from centralized config (not hardcoded)
- [ ] Routing keys documented in event docstrings
- [ ] Consumer has routing key mapping for all event types
- [ ] Exchanges, queues, and messages are durable/persistent
- [ ] Using `model_dump_json()` for serialization
- [ ] Error handling in consumer message processing
- [ ] Integration tests verify end-to-end event flow

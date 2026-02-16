# Use Case Test Harness Pattern

## Architecture

Use case tests validate end-to-end workflows by composing mock services that inherit from ABC interfaces.

**Structure:**
```
Tests → ITestHarness → MockTestHarness → Composes:
                                          - Mock Service 1 (inherits from ABC)
                                          - Mock Service 2 (inherits from ABC)
                                          - MockEventBus
```

---

## ITestHarness Interface

ITestHarness is a Python Protocol that abstracts test orchestration. It is **not** a service interface — it sits above services and coordinates them.

**Design principles:**
- **Simplified API**: Accepts plain arguments (e.g., `name: str`), not request DTOs. Harness implementations handle DTO conversion internally.
- **Async methods**: All methods are `async def` to support both mock and real (HTTP-based) implementations.
- **Test utilities**: Includes `get_published_events()`, `wait_for_events_processed()`, and `reset()` for test isolation.
- **Two implementations**: `MockTestHarness` (activity 04) for fast architect validation, `RealServiceHarness` (activity 06) for integration testing. Both implement the same Protocol — tests run unchanged against either.

---

## Mock Event Bus

Simple in-memory pub/sub for event communication between services:

```python
class MockEventBus:
    def __init__(self):
        self._subscribers: Dict[Type, List[Callable]] = defaultdict(list)
        self._published_events: List[BaseModel] = []

    def subscribe(self, event_type: Type[BaseModel], handler: Callable):
        self._subscribers[event_type].append(handler)

    def publish(self, event: BaseModel):
        self._published_events.append(event)
        for handler in self._subscribers[type(event)]:
            handler(event)

    def get_published_events(self) -> List[BaseModel]:
        return self._published_events.copy()
```

---

## Mock Service Implementation

Each service gets its own mock inheriting from the ABC interface:

```python
# use_case_tests/harnesses/mock_<service-name>_service.py
from architecture.contracts.<service-name>_service import (
    IServiceName,
    CreateResourceRequest,
    CreateResourceResponse,
    EVENTS_PUBLISHED,
    EVENTS_CONSUMED,
)

class MockServiceName(IServiceName):
    def __init__(self, event_bus: MockEventBus):
        self._event_bus = event_bus
        self._data: Dict[str, Dict] = {}
        # Subscribe to events in EVENTS_CONSUMED (if any)

    async def create_resource(self, request: CreateResourceRequest) -> CreateResourceResponse:
        # In-memory implementation
        ...
        # Publish events from EVENTS_PUBLISHED
        self._event_bus.publish(event)
        return response
```

**Key points:**
- Class inherits from the service's ABC interface
- Constructor accepts `event_bus` parameter
- Publish events listed in `EVENTS_PUBLISHED`
- Subscribe to events listed in `EVENTS_CONSUMED` (in constructor)
- Use in-memory data structures (dicts, lists) for state

---

## Mock Harness Orchestrator

Composes all mock services:

```python
class MockTestHarness(ITestHarness):
    def __init__(self):
        self._event_bus = MockEventBus()
        self._service_a = MockServiceA(self._event_bus)
        self._service_b = MockServiceB(self._event_bus)

    async def create_resource(self, name: str) -> CreateResourceResponse:
        request = CreateResourceRequest(name=name)
        return await self._service_a.create_resource(request)

    def get_published_events(self) -> List[BaseModel]:
        return self._event_bus.get_published_events()

    def reset(self):
        self._event_bus = MockEventBus()
        self._service_a = MockServiceA(self._event_bus)
        self._service_b = MockServiceB(self._event_bus)
```

**Key points:**
- Instantiate event bus first
- Inject event bus into all mock services
- Delegate harness methods to appropriate services
- Convert between simple types and DTOs where helpful
- Reset recreates all services with fresh state

---

## File Structure

```
use_case_tests/
├── harnesses/
│   ├── base_harness.py                 # ITestHarness interface
│   ├── mock_event_bus.py               # Event pub/sub
│   ├── mock_<service>_service.py       # One per service - inherits from ABC
│   └── mock_harness.py                 # Orchestrator
└── test_use_case_*.py                  # Tests written against ITestHarness
```

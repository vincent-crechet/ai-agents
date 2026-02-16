# Architecture Core: Service Implementation Guide

> **Document Scope:** This document defines the **internal, service-level architecture** and coding patterns. These principles MUST be applied by the Developer Agent when implementing the code for a single service inside its `services/{service-name}/` directory.
>
> For the high-level repository structure and agent workflow, refer to `CONTRIBUTING.md`.

---

## 0. Architecture-Level Contracts vs Service-Level Ports

**Two levels of interfaces exist in this architecture:**

1. **Architecture-Level Contracts** (`architecture/contracts/*.py`):
   - Define the **external API** each service exposes to other services/clients
   - Use Python `ABC` (Abstract Base Classes) to define service interfaces
   - Service implementations **must inherit** from these ABC interfaces
   - Contain Request/Response DTOs and Event definitions
   - Declare which events each service publishes/consumes
   - Created by the Architect in Activity 03b
   - **Purpose:** Define the contract between services with compile-time enforcement

2. **Service-Level Ports** (`services/{service}/app/ports/*.py`):
   - Define **internal dependencies** a service needs (database, message broker, external APIs)
   - Use abstract base classes (ABC) or Protocols
   - Implemented by Adapters (production and test implementations)
   - Created by the Developer during service implementation
   - **Purpose:** Enable dependency injection and testing

**Example:**
- `architecture/contracts/<service-name>_service.py` defines what a service provides to others (using ABC)
- `services/<service-name>/app/ports/repository.py` defines what a service needs internally (database access)

### Service Interface ABC Pattern

**Service implementations MUST inherit from their ABC interface:**

```python
# architecture/contracts/<service-name>_service.py
from abc import ABC, abstractmethod
from pydantic import BaseModel

class CreateResourceRequest(BaseModel):
    name: str

class CreateResourceResponse(BaseModel):
    id: str
    name: str

class IResourceService(ABC):
    """Service interface defining external API."""

    @abstractmethod
    async def create_resource(
        self, request: CreateResourceRequest
    ) -> CreateResourceResponse:
        """
        Create a new resource.

        Endpoint: POST /api/v1/resources
        HTTP Status: 201 Created
        """
        ...
```

```python
# services/<service-name>/app/services/resource_service.py
from architecture.contracts.<service-name>_service import (
    IResourceService,
    CreateResourceRequest,
    CreateResourceResponse,
)

class ResourceService(IResourceService):
    """Concrete implementation of IResourceService."""

    def __init__(self, repository: IResourceRepository):
        self.repository = repository

    async def create_resource(
        self, request: CreateResourceRequest
    ) -> CreateResourceResponse:
        # Implementation
        ...
```

**Benefits of ABC over Protocol:**
- Explicit inheritance makes contracts clear
- Runtime validation prevents incomplete implementations
- Cannot accidentally forget to implement required methods

### ⚠️ IMPORTANT: Architecture Contract Location

**Architecture contracts have a single source of truth:**
- **Repository root**: `architecture/contracts/*.py` (EDIT HERE)
- Services access these contracts directly during both development and Docker builds

**Docker Build Context:**
- The build script builds from repository root: `docker build -f services/{service}/Dockerfile -t {service}:test .`
- Dockerfiles copy contracts directly: `COPY architecture/ ./architecture/`
- No synchronization needed - contracts are always current

**Development:**
- Services import from repository root using `PYTHONPATH=/path/to/repo:$PYTHONPATH`
- Example: `from architecture.contracts.common import SomeSharedEvent`

---

## 1. Hexagonal Architecture (Ports and Adapters)

**The Rule:** Core business logic (services) must NEVER depend on concrete infrastructure implementations. Services depend only on abstract **Ports** (interfaces), which are implemented by **Adapters**. Dependency Injection wires them together.

---

## 2. The Four-Step Dependency Injection Pattern

Follow this pattern for every external dependency (databases, message queues, other services).

1.  **Define the Port (Interface):** Create an abstract class in `app/ports/`.
2.  **Create Adapters:** Create at least two implementations in `app/adapters/`: a production adapter (e.g., `PostgresRepository`) and a test adapter (e.g., `InMemoryRepository`).
3.  **Inject Interface into Services:** Services in `app/services/` must only depend on the Port (interface), never the concrete adapter.
4.  **Wire Dependencies (Composition Root):** Use the `app/dependencies.py` file to choose which concrete adapter to inject at runtime.

---

## 3. Synchronous vs. Asynchronous Communication

-   **Use Sync (Request-Response)** for queries or fast commands where the client needs an immediate answer. Return `200 OK` or `201 Created`.
-   **Use Async (Fire-and-Forget)** for long-running tasks. Your API should return `202 Accepted` immediately, and the work should be done in the background.

---

## 4. Multi-Tenancy (If Applicable)

If your application serves multiple isolated customers (tenants), all repository queries must automatically filter by `tenant_id`. This filtering should be enforced at the adapter level, not in the service logic.

---

## 5. Error Handling

Define domain-specific exceptions in `app/exceptions/`. The API layer in `app/main.py` should map these custom exceptions to appropriate HTTP status codes (e.g., `404 Not Found`, `409 Conflict`).

---

## 6. Configuration Management

Use an environment-aware settings class (e.g., using Pydantic's `BaseSettings`) in `app/config.py` to manage configuration for different environments like local development, testing, and production.

---

## 7. Service-Level Testing Strategy

This strategy applies to the tests written by the Developer Agent inside the `services/{service-name}/tests/` directory.

### Unit Tests (Fast, No External Dependencies)

-   **Location:** `tests/unit/`
-   **Method:** Test your service classes by injecting **in-memory adapters**. These tests must be fast and self-contained. They prove the business logic is correct.

### Local Integration Tests (With Real Infrastructure)

-   **Location:** `tests/integration/`
-   **Method:** Test your adapters against real infrastructure (e.g., a PostgreSQL database running in Docker). These tests prove your adapter correctly communicates with the external service.

> **Note:** The end-to-end testing of cross-service business workflows is defined in `CONTRIBUTING.md` and implemented in the `/use_case_tests` directory.

---

## 8. Internal Service Structure (`app/` directory)

This structure MUST be followed inside the `app/` directory of every service.

```plaintext
app/
├── main.py                    # Application entry point (e.g., FastAPI app)
├── config.py                  # Settings and environment configuration
├── dependencies.py            # Dependency injection wiring (composition root)
│
├── models/                    # Domain entities / Pydantic models
├── ports/                     # Abstract interfaces for external dependencies
├── adapters/                  # Concrete implementations of ports (DB, message bus, etc.)
├── services/                  # Core business logic
├── api/                       # HTTP endpoints and request/response models
└── exceptions/                # Custom domain-specific exceptions
```

---

## 9. Code Quality Standards

-   **Naming Conventions:** Interfaces are prefixed with `I` (e.g., `IProductRepository`).
-   **Type Hints:** All function and method signatures must have full type hints.
-   **Documentation:** All public modules, classes, and functions must have docstrings explaining their purpose.

---

## 10. Implementation Checklist

When implementing a feature in a service:

-   [ ] Define Port(s) for any new external dependency in `app/ports/`.
-   [ ] Create production and in-memory adapters in `app/adapters/`.
-   [ ] Write the service logic in `app/services/` depending only on Ports.
-   [ ] Expose functionality via the `app/api/` layer.
-   [ ] Write unit tests with in-memory adapters in `tests/unit/`.
-   [ ] Write local integration tests for new adapters in `tests/integration/`.
-   [ ] Ensure all code is fully type-hinted and documented.

---

## 11. Quick Reference: Inside a Service

| What              | Where It Goes (within the service) |
| ----------------- | ---------------------------------- |
| Domain models     | `app/models/`                      |
| Interfaces        | `app/ports/`                       |
| Production code   | `app/adapters/`, `app/services/`   |
| Test adapters     | `app/adapters/` (e.g., in-memory)  |
| HTTP endpoints    | `app/api/`                         |
| DI setup          | `app/dependencies.py`              |
| Unit tests        | `tests/unit/`                      |
| Integration tests | `tests/integration/`               |

---

## 12. When to Deviate

These principles are the default. If a specific technical challenge requires a deviation, the reason MUST be documented in a `DECISIONS.md` file within the service's root directory.
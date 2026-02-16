# Service Production Readiness

Critical requirements for production-ready service implementation.

---

## Database Sessions

**MUST:** Use `AsyncGenerator` with `async with` for database sessions to ensure automatic cleanup.

**MUST NOT:** Create sessions without guaranteed cleanup (causes connection leaks).

---

## Logging

**MUST:** Use Python's `logging` module with `logger.warning()`, `logger.error()`, etc.

**MUST:** Include structured context using `extra={}` parameter for log aggregation.

**MUST NOT:** Use `print()` statements for logging.

---

## Datetime Handling

**MUST:** Use `datetime.now(timezone.utc)` for UTC timestamps (timezone-aware).

**MUST:** Use SQLAlchemy `TIMESTAMP(timezone=True)` for datetime columns (supports timezone-aware datetimes).

**MUST NOT:** Use deprecated `datetime.utcnow()` (removed in Python 3.12+).

**MUST NOT:** Use `DateTime` column type with timezone-aware datetimes (causes PostgreSQL compatibility issues).

---

## HTTP Request Context

**MUST:** Extract `user_agent` from `request.headers.get("user-agent")` for analytics.

**MUST:** Extract `ip_address` from `request.client.host` when available.

**MUST:** Pass request context to service layer when publishing events.

---

## HTTP Status Codes

**MUST:** Return `201 Created` for newly created resources.

**MUST:** Return `200 OK` when returning existing resources (e.g., deduplication).

**MUST NOT:** Always return the same status code regardless of operation result.

---

## Exception Handling

**MUST:** Use string values for HTTPException `detail` parameter.

**MUST:** Map domain exceptions to appropriate HTTP status codes in exception handlers.

**MUST NOT:** Use dictionaries or objects for HTTPException `detail` (causes serialization issues).

---

## Input Validation

**MUST:** Place business validation rules (e.g., limit must be positive) in the service layer and raise domain exceptions.

**MUST NOT:** Duplicate business validation as FastAPI Query/Path constraints (e.g., `Query(ge=1)`). FastAPI returns 422 for constraint violations, bypassing domain exceptions and producing inconsistent error responses.

---

## Dependency Injection

**MUST:** Use FastAPI's `Depends()` for injecting dependencies into route handlers.

**MUST:** Ensure dependencies with resources (DB sessions, connections) use generators with proper cleanup.

**MUST NOT:** Manually call dependency functions or manage lifecycle in route handlers.

---

## Event Handler Session Management

**MUST:** Persist changes in event handlers by calling the repository port's `commit()` method.

**MUST:** Create a fresh database session per event in the adapter layer for isolation.

**MUST NOT:** Access the adapter's internal session from the service layer (e.g., `self.repository.session.commit()`). This breaks the port abstraction and silently fails for in-memory adapters.

---

## Health Endpoint

**MUST:** Expose `GET /health` returning `{"status": "healthy"}` with status 200.

**MUST:** Keep the endpoint lightweight — no database queries or external calls.

**MUST NOT:** Require authentication for the health endpoint (used by Docker health checks and load balancers).

**MUST:** Register `/health` BEFORE any catch-all route (e.g., `/{path_param}`). FastAPI matches routes in registration order — a catch-all registered first will intercept `/health` and return 404.

---

## Database Table Initialization

**MUST:** Create database tables on startup in the lifespan handler using `Base.metadata.create_all`. This ensures tables exist in containerized deployments without requiring external migration tools.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # ... rest of lifespan
```

**MUST NOT:** Rely on test fixtures or external scripts for table creation in production/Docker environments.

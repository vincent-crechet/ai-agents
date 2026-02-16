# Technical Stack

Products and versions to use across all services.

---

## Core Stack

| Layer | Product | Version | Notes |
|-------|---------|---------|-------|
| Language | Python | `3.11` in Docker, `^3.10` in pyproject.toml | |
| API Framework | FastAPI | `^0.109.0` | Must support Pydantic V2 |
| Web Server | Uvicorn | `^0.27.0` | Standard extras |
| Data Validation | Pydantic | `^2.5.0` | V2 — see API notes below |
| Configuration | pydantic-settings | `^2.1.0` | |
| Interface Definitions | `abc.ABC` | stdlib | Service contracts |
| Database | PostgreSQL | `15+` | |
| ORM | SQLAlchemy | `^2.0.25` | Async only |
| DB Driver (async) | asyncpg | `^0.29.0` | Production |
| DB Driver (sync) | psycopg2-binary | `^2.9.9` | Integration tests |
| Message Broker | RabbitMQ | `3+` | Management plugin required |
| Messaging (async) | aio-pika | `^9.3.1` | Production |
| Messaging (sync) | pika | `^1.3.2` | Integration tests |
| Build Tool | Poetry | `2.0.1` | Dockerfile build stage only. **`--no-dev` removed in 2.0 — use `--only main`** |
| Architecture | Hexagonal | — | Ports & Adapters |

## Testing Stack

| Product | Version | Purpose |
|---------|---------|---------|
| pytest | `^7.4.3` | Test framework |
| pytest-asyncio | `^0.21.1` | Async test support |
| pytest-cov | `^4.1.0` | Coverage reporting |
| testcontainers | `^3.7.1` | Docker-based integration tests |
| httpx | `^0.26.0` | HTTP client for tests |
| docker | `^7.0.0` | Docker SDK (used by testcontainers) |

Testing dependencies go in `[tool.poetry.group.dev.dependencies]`.

---

## Docker Base Images

```yaml
# Services
python:3.11-slim        # Multi-stage Dockerfile base

# Infrastructure
postgres:15-alpine
rabbitmq:3-management-alpine
```

---

## Critical API Patterns

### Pydantic V2 Serialization

```python
# ❌ WRONG — Pydantic V1 style
response = result.dict()

# ✅ CORRECT — Pydantic V2
response = result.model_dump(mode='json')
```

`mode='json'` is required to correctly serialize `datetime`, `UUID`, `Decimal` etc. Use it for `JSONResponse` content and message broker payloads.

See `07_pydantic_v2_guidelines.md` for full details.

### Event Serialization

```python
message_body = event.model_dump_json().encode()
```

### FastAPI Response Models

```python
# Let FastAPI handle serialization
@app.post("/api/resource", response_model=ResponseModel)
async def create() -> ResponseModel:
    return service.create()

# Manual JSONResponse for custom status codes
@app.post("/api/resource")
async def create():
    result = service.create()
    return JSONResponse(
        content=result.model_dump(mode='json'),
        status_code=201
    )
```

# Analytics Service

Tracks URL access statistics for the URL shortener. Consumes `UrlAccessedEvent` messages from RabbitMQ and provides an API to query the most accessed URLs.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/stats/top?limit=10` | Return top accessed URLs ranked by count |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/analytics` | PostgreSQL connection string |
| `RABBITMQ_URL` | `amqp://guest:guest@localhost:5672/` | RabbitMQ connection string |
| `RABBITMQ_EXCHANGE` | `url_shortener` | RabbitMQ exchange name |
| `SERVICE_NAME` | `analytics` | Service name for queue naming |

## Running

```bash
# Development
PYTHONPATH=/path/to/repo uvicorn app.main:app --reload

# Tests
PYTHONPATH=/path/to/repo python -m pytest tests/unit/ -v
PYTHONPATH=/path/to/repo python -m pytest tests/integration/ -v
```

# URL Management Service

Service for shortening long URLs into deterministic short codes and resolving them back to the original URLs.

## Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | /api/v1/urls | Shorten a long URL | 201 Created / 200 OK |
| GET | /{short_code} | Redirect to original URL | 301 Moved Permanently |
| GET | /health | Health check | 200 OK |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql+asyncpg://postgres:postgres@localhost:5432/url_management | PostgreSQL connection string |
| RABBITMQ_URL | amqp://guest:guest@localhost:5672/ | RabbitMQ connection string |
| RABBITMQ_EXCHANGE | url_shortener | RabbitMQ exchange name |
| BASE_URL | http://localhost:8000 | Base URL for generated short URLs |

## Running

```bash
# Development
PYTHONPATH=/path/to/repo uvicorn app.main:app --reload

# Docker
docker build -f services/url-management/Dockerfile -t url-management:latest .
docker run -p 8000:8000 url-management:latest

# Tests
PYTHONPATH=/path/to/repo python -m pytest tests/unit/ -v
PYTHONPATH=/path/to/repo python -m pytest tests/integration/ -v
```

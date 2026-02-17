FROM python:3.11-slim AS builder

WORKDIR /build

RUN pip install poetry==2.0.1

COPY services/analytics/pyproject.toml services/analytics/poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY services/analytics/app/ ./app/
COPY architecture/ ./architecture/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Integration Test Infrastructure

Patterns for running use case tests against real containerized services.

---

## RealServiceHarness

Implements ITestHarness by making HTTP requests to real services:

- Use `httpx.Client` for HTTP requests to services
- Map each ITestHarness method to its corresponding service HTTP endpoint (read base_harness.py and service API routes)
- Parse response JSON into DTO types from architecture/contracts/
- Map HTTP errors to Python exceptions (404 → KeyError, 400 → ValueError)
- Store service URLs, database URLs (for cleanup/event verification), and message broker management URL

### reset() Implementation

- Use `DELETE FROM <table>` instead of `TRUNCATE TABLE <table> CASCADE` — TRUNCATE requires ACCESS EXCLUSIVE lock which deadlocks against open service transactions
- Purge message broker queues via management API
- Use `sqlalchemy.pool.NullPool` for all `create_engine()` calls to prevent connection pool threads from keeping the process alive after tests

### Event Verification

- `get_published_events()`: Query service databases directly for event records
- `wait_for_events_processed()`: Poll service databases until events are consumed

---

## Docker Compose Configuration

For each service discovered from architecture/services.yml:

- Define a PostgreSQL container and the service container
- Add infrastructure containers (e.g., message broker) based on event routing in contracts
- Use a shared bridge network for inter-service communication
- Assign non-conflicting host ports to avoid clashes with local installations
- Expose database and message broker management ports for test harness access from host
- Add health checks for infrastructure containers
- Use `depends_on` with `condition: service_healthy` for startup ordering

---

## Conftest Fixtures

### docker_compose_services (session scope)

- Setup: `docker compose down` (cleanup prior crashed runs), then `docker compose up -d --wait`, then `wait_for_service_health()` per service
- Teardown: `docker compose down`
- Session-scoped: one startup for the entire test run; `reset()` between tests handles isolation

### integration_test_harness (function scope)

- Depends on docker_compose_services
- Creates RealServiceHarness with localhost URLs matching docker-compose.test.yml port mappings
- Teardown: call `harness.reset()` and `harness.client.close()`

### wait_for_service_health()

- Default timeout: 90 seconds
- Progress logging every 10 seconds
- Capture and display last error on timeout

### Important

- KEEP existing test_harness fixture (MockTestHarness for fast tests)
- KEEP existing pytest_addoption and pytest_configure hooks

---

## Docker Build Script

- Build from repository root using `-f` flag: `docker build -f services/<service>/Dockerfile -t <service>:test .`
- Include warnings that images are snapshots and must be rebuilt after code changes
- See `09_architecture_contract_synchronization.md` for build context details

---

## Troubleshooting

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| Tests timeout waiting for health | Stale Docker images or service startup errors | Rebuild images; check container logs |
| Service crashes with UnboundLocalError | Duplicate imports inside functions | Remove function-level imports; keep module-level only |
| ModuleNotFoundError: 'architecture' | Dockerfile not copying architecture/ | Verify `COPY architecture/ ./architecture/`; build from repo root |
| Connection refused to database | PostgreSQL not ready | Check healthcheck config; increase retries |
| Message broker connection errors | Broker not ready when services start | Check `depends_on` with `service_healthy`; increase start_period |
| Service still crashes after fix | Forgot to rebuild images | Always rebuild: `./build_test_images.sh` |
| Process hangs after tests PASSED | Connection pool threads or unclosed clients | Use NullPool; close httpx client in teardown; use DELETE FROM not TRUNCATE |
| Port already in use | Leftover containers from crashed run | `docker compose down`; conftest does this automatically on setup |
| Docker Compose up "fails" but containers are running | `docker compose up -d --wait` sends ALL output to stderr, even on success | Check exit code only — do not treat non-empty stderr as failure |
| Health check returns 404 | Catch-all route `/{param}` registered before `/health` | Register `/health` before including routers with catch-all paths |

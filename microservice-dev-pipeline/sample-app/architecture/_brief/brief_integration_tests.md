# Developer Brief: Integration Tests

_Created: 2026-02-07_
_Activity: 06_Developer_integration_tests_

## Objective

Create integration test infrastructure to run use case tests against real containerized services via Docker Compose.

## Summary

Built a RealServiceHarness that implements the same ITestHarness protocol as MockTestHarness, but delegates to real services via HTTP. All 10 use case tests pass in both mock mode (0.09s) and integration mode (67s) using the same test code.

## Generated Artifacts

### Harness
- **File:** `use_case_tests/harnesses/real_service_harness.py`
- **Purpose:** ITestHarness implementation using httpx for HTTP requests, sqlalchemy for DB cleanup/verification, and RabbitMQ management API for queue purging.

### Infrastructure
- **File:** `use_case_tests/docker-compose.test.yml`
- **Purpose:** Docker Compose config with 5 containers (2 services, 2 databases, 1 message broker) on a shared bridge network with health checks.

- **File:** `use_case_tests/build_test_images.sh`
- **Purpose:** Builds Docker images for both services from repository root.

- **File:** `use_case_tests/run_integration_tests.sh`
- **Purpose:** One-command script to build images and run integration tests.

### Test Configuration
- **File:** `use_case_tests/conftest.py`
- **Purpose:** Updated with docker_compose_services (session-scoped) and dual-mode test_harness fixture (mock vs integration via --integration flag).

- **File:** `use_case_tests/pytest.ini`
- **Purpose:** Registers integration marker and sets asyncio mode.

### Documentation
- **File:** `use_case_tests/README.md`
- **Purpose:** Documents both test modes, port mappings, and troubleshooting.

## Change Record

- **Trigger:** Initial development (greenfield) — upstream from `architecture/_brief/brief_service_implementation.md`
- **Artifacts created:** `use_case_tests/harnesses/real_service_harness.py`, `use_case_tests/docker-compose.test.yml`, `use_case_tests/build_test_images.sh`, `use_case_tests/run_integration_tests.sh`, `use_case_tests/pytest.ini`, `use_case_tests/README.md`
- **Artifacts modified:** `use_case_tests/conftest.py` (added integration fixtures), `services/url-management/app/main.py` (health route ordering, table creation on startup), `services/analytics/app/main.py` (table creation on startup), `services/url-management/Dockerfile` (Poetry 2.0 flag fix)
- **Artifacts reviewed, no change needed:** `use_case_tests/harnesses/base_harness.py`, all test files, `architecture/contracts/*.py`

## Key Decisions Made

- **Decision:** Health endpoint registered before catch-all `/{short_code}` route in url-management.
- **Rationale:** FastAPI matches routes in registration order; the catch-all was intercepting `/health`.

- **Decision:** Use `DELETE FROM` instead of `TRUNCATE TABLE` for reset().
- **Rationale:** TRUNCATE requires ACCESS EXCLUSIVE lock which deadlocks against open service transactions.

- **Decision:** Table creation added to service lifespan startup.
- **Rationale:** Required for containerized deployment; no migration tool (Alembic) configured yet.

## Sign-Off

**Status:** ✓ Complete
**Artifacts Created:** 6 new files, 4 files modified
**Coverage:** 10/10 use case tests pass in both mock and integration modes
**Ready for:** Production deployment planning

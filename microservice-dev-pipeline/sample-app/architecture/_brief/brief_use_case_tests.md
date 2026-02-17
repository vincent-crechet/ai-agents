# Architect Brief: Use Case Tests

_Created: 2026-02-07_
_Activity: 04_Architect_use_case_tests_

## Objective

Create executable end-to-end tests with mock harness infrastructure to validate service contracts against use case acceptance criteria.

## Summary

Built a complete mock harness infrastructure (event bus, mock services for both url-management and analytics, orchestrator) and 10 test cases covering all 3 use cases. All tests pass against the MockTestHarness implementation.

## Generated Artifacts

### Harness Infrastructure
- **File:** `use_case_tests/harnesses/base_harness.py`
- **Purpose:** `ITestHarness` Protocol defining the simplified async API for tests.

- **File:** `use_case_tests/harnesses/mock_event_bus.py`
- **Purpose:** In-memory pub/sub event bus for mock service communication.

- **File:** `use_case_tests/harnesses/mock_url_management_service.py`
- **Purpose:** Mock implementation of `IUrlManagementService` with in-memory storage and deterministic short code generation.

- **File:** `use_case_tests/harnesses/mock_analytics_service.py`
- **Purpose:** Mock implementation of `IAnalyticsService` that subscribes to `UrlAccessedEvent` and tracks access counts.

- **File:** `use_case_tests/harnesses/mock_harness.py`
- **Purpose:** `MockTestHarness` orchestrator composing all mock services with shared event bus.

### Test Configuration
- **File:** `use_case_tests/conftest.py`
- **Purpose:** Provides `test_harness` fixture returning `MockTestHarness`.

### Test Cases
- **File:** `use_case_tests/test_use_case_001_shorten_url.py`
- **Purpose:** 3 tests validating URL shortening, idempotency, and uniqueness.

- **File:** `use_case_tests/test_use_case_002_redirect_via_short_url.py`
- **Purpose:** 3 tests validating redirect, not-found error, and UrlAccessedEvent publishing.

- **File:** `use_case_tests/test_use_case_003_view_most_accessed_urls.py`
- **Purpose:** 4 tests validating ranked stats, empty state, limit parameter, and entry completeness.

## Change Record

- **Trigger:** Initial development (greenfield) — upstream from `architecture/_brief/brief_service_interface_definition.md`
- **Artifacts created:** All files listed above (10 files)
- **Artifacts modified:** None
- **Artifacts reviewed, no change needed:** `architecture/contracts/*.py`, `architecture/workflows/*.md`, `product/use_cases/*.md`

## Key Decisions Made

- **Decision:** `UrlNotFoundError` exception defined in mock service, to be mirrored in real implementation.
- **Rationale:** Tests need a concrete exception type to assert against; the real service will define its own domain exception.

## Next Steps for Developer (Activity 05)

1. **Read:** `architecture/contracts/*.py` — implement services inheriting from these ABCs
2. **Read:** `product/<service>_service/REQ_*.md` — understand functional requirements
3. **Read:** `use_case_tests/harnesses/mock_*.py` — understand expected behavior (tests must pass against real services too in activity 06)
4. **Implement:** Each service in `services/<service-name>/` following hexagonal architecture

## Sign-Off

**Status:** ✓ Complete
**Artifacts Created:** 10 files
**Coverage:** All 3 use cases covered, 10 tests passing
**Ready for:** Developer (Activity 05 - Service Implementation)

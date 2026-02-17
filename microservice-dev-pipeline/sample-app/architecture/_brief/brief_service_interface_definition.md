# Architect Brief: Service Interface Definition

_Created: 2026-02-07_
_Activity: 03b_Architect_service_interface_definition_

## Objective

Generate Python contract files defining service interface ABCs, DTOs, events, and event routing for all services.

## Summary

Created three contract files: a shared `common.py` with the `UrlAccessedEvent`, and per-service contract files defining ABC interfaces, request/response DTOs, and event routing declarations. All workflow interactions have corresponding ABC methods.

## Generated Artifacts

### Shared Contracts
- **File:** `architecture/contracts/__init__.py`
- **Purpose:** Package initializer.

- **File:** `architecture/contracts/common.py`
- **Purpose:** Shared event definitions (`UrlAccessedEvent`) used across services.

### Service Contracts
- **File:** `architecture/contracts/url_management_service.py`
- **Purpose:** Interface contract for url-management: `IUrlManagementService` ABC with `shorten_url` and `resolve_url` methods, DTOs, and event routing.

- **File:** `architecture/contracts/analytics_service.py`
- **Purpose:** Interface contract for analytics: `IAnalyticsService` ABC with `get_top_urls` and `handle_url_accessed` methods, DTOs, and event routing.

## Change Record

- **Trigger:** Initial development (greenfield) — upstream from `product/_brief/brief_service_decomposition.md`
- **Artifacts created:** `architecture/contracts/__init__.py`, `architecture/contracts/common.py`, `architecture/contracts/url_management_service.py`, `architecture/contracts/analytics_service.py`
- **Artifacts modified:** None
- **Artifacts reviewed, no change needed:** `architecture/services.yml`, all workflow files, all use case files

## Key Decisions Made

- **Decision:** Single shared event (`UrlAccessedEvent`) in `common.py` rather than duplicating in each service contract.
- **Rationale:** The event is the contract between services; a single definition ensures both sides agree on the schema.

- **Decision:** `resolve_url` returns a `ResolveUrlResponse` DTO rather than a raw string.
- **Rationale:** Consistent with the ABC pattern; allows future extension without breaking the interface.

## Next Steps for Architect (Activity 04)

1. **Read:** `architecture/contracts/*.py` — understand all service interfaces and DTOs
2. **Read:** `product/use_cases/*.md` — understand acceptance criteria to test
3. **Create:** Use case test files in `use_case_tests/` using the contract ABCs for test harnesses

## Sign-Off

**Status:** ✓ Complete
**Artifacts Created:** 4 files
**Coverage:** 2/2 services have contract files, all workflow interactions covered
**Ready for:** Architect (Activity 04 - Use Case Tests)

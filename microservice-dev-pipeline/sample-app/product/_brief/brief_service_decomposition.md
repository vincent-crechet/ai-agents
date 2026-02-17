# Architect Brief: Service Decomposition

_Created: 2026-02-07_
_Activity: 02_Architect_service_decomposition_

## Objective

Decompose the ShortURL product into services with clear bounded contexts and define integration workflows for all use cases.

## Summary

The product is decomposed into two services: **url-management** (shortening, storage, redirection) and **analytics** (access tracking, statistics dashboard). They communicate asynchronously via a UrlAccessedEvent published by url-management when a short URL is resolved.

## Generated Artifacts

### Service Definitions
- **File:** `architecture/services.yml`
- **Purpose:** Defines the two services, their owned entities, published/consumed events, and use case assignments.

### Workflows
- **File:** `architecture/workflows/workflow_001_shorten_url.md`
- **Purpose:** Synchronous workflow for URL shortening (url-management only).

- **File:** `architecture/workflows/workflow_002_redirect_via_short_url.md`
- **Purpose:** Hybrid workflow for URL redirection with async event to analytics.

- **File:** `architecture/workflows/workflow_003_view_most_accessed_urls.md`
- **Purpose:** Synchronous workflow for querying most accessed URLs (analytics only).

## Change Record

- **Trigger:** Initial development (greenfield) — upstream from `architecture/_brief/brief_product_definition.md`
- **Artifacts created:** `architecture/services.yml`, `architecture/workflows/workflow_001_shorten_url.md`, `architecture/workflows/workflow_002_redirect_via_short_url.md`, `architecture/workflows/workflow_003_view_most_accessed_urls.md`
- **Artifacts modified:** None
- **Artifacts reviewed, no change needed:** `product/product_definition.md`, all use case files in `product/use_cases/`

## Key Decisions Made

- **Decision:** Two services (url-management + analytics) rather than three or a monolith.
- **Rationale:** Shortening and redirection share the URL mapping entity and are tightly coupled. Analytics has a different bounded context (access statistics) and different consumer (web dashboard vs API).

- **Decision:** Hybrid communication for redirect workflow (sync redirect + async event).
- **Rationale:** Redirect must be low-latency for End Users, while analytics processing can be eventually consistent. Async decoupling prevents analytics load from affecting redirect performance.

## Next Steps for Product Owner (Activity 03a) and Architect (Activity 03b)

1. **Read:** `architecture/services.yml` — understand service boundaries and owned entities
2. **Read:** All workflow files in `architecture/workflows/` — understand service interactions
3. **03a (PO):** Create service requirements (REQ_*.md) for each service
4. **03b (Architect):** Create service interface contracts (`architecture/contracts/*.py`)

## Sign-Off

**Status:** ✓ Complete
**Artifacts Created:** 4 files
**Coverage:** All 3 use cases have corresponding workflows, all 2 services defined
**Ready for:** Product Owner (Activity 03a) and Architect (Activity 03b) — parallel execution

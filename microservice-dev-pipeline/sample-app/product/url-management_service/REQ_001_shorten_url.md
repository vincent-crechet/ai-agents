# REQ-001: Shorten URL

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

## ID
REQ-001

## Title
Shorten a long URL into a deterministic short URL

## Parent Use Case
[UC-001 Shorten a URL](../../use_cases/use_case_001_shorten_url.md)

## Requirement
As the **url-management** service, I want to **accept a long URL and return a deterministic short URL**, so that **API consumers can generate consistent, shareable short links**.

## Acceptance Criteria

- [ ] **Given** a valid long URL, **when** the service receives a POST request to `/api/v1/urls` with the long URL in the request body, **then** the service **MUST** return a response containing the generated short URL and the original long URL.
- [ ] **Given** the same long URL submitted multiple times, **when** the service receives each request, **then** the service **MUST** return the same short URL every time (idempotent).
- [ ] **Given** a long URL that has already been shortened, **when** the service receives a request for it, **then** the service **MUST** return the existing short URL rather than creating a duplicate mapping.
- [ ] **Given** an invalid URL (malformed, empty, or missing), **when** the service receives the request, **then** the service **MUST** return an error response indicating invalid input.
- [ ] **Given** a successful shortening, **then** the service **MUST** persist the mapping between the short code and the long URL for future resolution.

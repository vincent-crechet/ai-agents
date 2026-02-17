# REQ-002: Redirect via Short URL

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

## ID
REQ-002

## Title
Resolve a short URL and redirect to the original long URL

## Parent Use Case
[UC-002 Redirect via Short URL](../../use_cases/use_case_002_redirect_via_short_url.md)

## Requirement
As the **url-management** service, I want to **resolve a short code to the original long URL and redirect the user**, so that **end users can reach the original destination via the short link**.

## Acceptance Criteria

- [ ] **Given** a valid short code, **when** the service receives a GET request to `/{short_code}`, **then** the service **MUST** return a redirect response pointing to the original long URL.
- [ ] **Given** a short code that does not exist, **when** the service receives the request, **then** the service **MUST** return an error response indicating the short URL was not found.
- [ ] **Given** a successful redirect, **then** the service **MUST** publish a `UrlAccessedEvent` containing the short code and the long URL.

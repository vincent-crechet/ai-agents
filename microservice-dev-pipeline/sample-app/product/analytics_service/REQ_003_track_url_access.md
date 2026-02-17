# REQ-003: Track URL Access

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

## ID
REQ-003

## Title
Track URL access events and maintain access counts

## Parent Use Case
[UC-002 Redirect via Short URL](../../use_cases/use_case_002_redirect_via_short_url.md)

## Requirement
As the **analytics** service, I want to **consume URL access events and maintain access counts**, so that **the most accessed URLs can be reported to dashboard users**.

## Acceptance Criteria

- [ ] **Given** a `UrlAccessedEvent` is received, **when** the service processes it, **then** the service **MUST** increment the access count for the corresponding short URL.
- [ ] **Given** a `UrlAccessedEvent` for a URL not yet tracked, **when** the service processes it, **then** the service **MUST** create a new access statistics record with an access count of 1.
- [ ] **Given** the event contains a short code and long URL, **then** the service **MUST** store both for later retrieval in the statistics view.

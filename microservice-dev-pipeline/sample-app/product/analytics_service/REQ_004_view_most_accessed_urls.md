# REQ-004: View Most Accessed URLs

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

## ID
REQ-004

## Title
Serve the most accessed URLs ranked by access count

## Parent Use Case
[UC-003 View Most Accessed URLs](../../use_cases/use_case_003_view_most_accessed_urls.md)

## Requirement
As the **analytics** service, I want to **provide the most accessed URLs ranked by access count**, so that **dashboard users can see which links are most popular**.

## Acceptance Criteria

- [ ] **Given** URLs have been accessed, **when** the service receives a GET request to `/api/v1/stats/top`, **then** the service **MUST** return a list of URLs ranked by access count in descending order.
- [ ] **Given** the response, **then** each entry **MUST** contain the short code, the original long URL, and the access count.
- [ ] **Given** no URLs have been accessed yet, **when** the service receives the request, **then** the service **MUST** return an empty list.
- [ ] **Given** a request with an optional `limit` query parameter, **when** the service receives it, **then** the service **MUST** return at most that many entries (defaulting to a reasonable number if not specified).

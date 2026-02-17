# Use Case 002: Redirect via Short URL

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

## ID
UC-002

## Title
Redirect via Short URL

## Actors
- End User

## Happy Path
1. The End User accesses a short URL.
2. The system looks up the original long URL associated with the short URL.
3. The system redirects the End User to the original long URL.

## Acceptance Criteria

- [ ] Given a valid short URL, when the End User accesses it, then the End User is redirected to the original long URL.
- [ ] Given a short URL that does not exist, when the End User accesses it, then the End User sees an error message indicating the link was not found.

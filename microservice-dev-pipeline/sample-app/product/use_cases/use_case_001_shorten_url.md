# Use Case 001: Shorten a URL

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

## ID
UC-001

## Title
Shorten a URL

## Actors
- API Consumer

## Happy Path
1. The API Consumer submits a long URL to the shortening service.
2. The system generates a deterministic short URL for the provided long URL.
3. The system returns the short URL to the API Consumer.

## Acceptance Criteria

- [ ] Given a valid long URL, when the API Consumer submits it for shortening, then the API Consumer receives a short URL.
- [ ] Given the same long URL submitted multiple times, when the API Consumer submits it, then the API Consumer always receives the same short URL.
- [ ] Given an invalid or empty URL, when the API Consumer submits it for shortening, then the API Consumer receives a clear error message indicating the input is invalid.

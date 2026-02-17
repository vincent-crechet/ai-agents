# Workflow 002: Redirect via Short URL

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

**Use Case:** [../../product/use_cases/use_case_002_redirect_via_short_url.md](../../product/use_cases/use_case_002_redirect_via_short_url.md)

---

## Overview

A hybrid workflow where an End User accesses a short URL, gets redirected synchronously, and the access is recorded asynchronously for analytics.

---

## Participating Services

- **url-management**: Resolves the short code to the original long URL, redirects the End User, and publishes a UrlAccessedEvent.
- **analytics**: Consumes the UrlAccessedEvent and increments the access counter for that URL.

---

## Sequence of Operations

```
┌──────────┐          ┌──────────────────┐          ┌────────────┐
│ End User │          │  url-management   │          │  analytics  │
└────┬─────┘          └────────┬──────────┘          └──────┬─────┘
     │                         │                            │
     │ GET /{short_code}       │                            │
     ├────────────────────────>│                            │
     │                         │                            │
     │ 301 Redirect {long_url} │  UrlAccessedEvent (async)  │
     │<────────────────────────┤───────────────────────────>│
     │                         │                            │
```

---

## Service Interaction Pattern

- **Synchronous**: The End User receives an immediate redirect response from url-management. Low latency is critical for redirection.
- **Asynchronous**: url-management publishes a UrlAccessedEvent after resolving the URL. The analytics service consumes this event to update access counts. This decouples the performance-critical redirect path from analytics processing.

# Workflow 003: View Most Accessed URLs

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

**Use Case:** [../../product/use_cases/use_case_003_view_most_accessed_urls.md](../../product/use_cases/use_case_003_view_most_accessed_urls.md)

---

## Overview

A synchronous request-response workflow where a Dashboard User requests the most accessed URLs from the analytics service and receives a ranked list.

---

## Participating Services

- **analytics**: Queries its access statistics and returns the most accessed URLs ranked by access count.

---

## Sequence of Operations

```
┌────────────────┐          ┌────────────┐
│ Dashboard User │          │  analytics  │
└───────┬────────┘          └──────┬─────┘
        │                          │
        │ GET /api/v1/stats/top    │
        ├─────────────────────────>│
        │                          │
        │ 200 OK {ranked_urls}     │
        │<─────────────────────────┤
        │                          │
```

---

## Service Interaction Pattern

- **Synchronous**: The entire workflow is synchronous request-response. The Dashboard User queries pre-aggregated statistics, which is a fast read operation.
- **Asynchronous**: None — data was already aggregated asynchronously via UrlAccessedEvent in Workflow 002.

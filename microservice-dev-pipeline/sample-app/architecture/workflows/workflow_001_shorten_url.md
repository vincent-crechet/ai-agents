# Workflow 001: Shorten a URL

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | 2026-02-07 | Initial development | Created | — |

**Use Case:** [../../product/use_cases/use_case_001_shorten_url.md](../../product/use_cases/use_case_001_shorten_url.md)

---

## Overview

A synchronous request-response workflow where an API Consumer submits a long URL and receives a deterministic short URL. Only the url-management service participates.

---

## Participating Services

- **url-management**: Receives the long URL, generates a deterministic short code, persists the mapping, and returns the short URL.

---

## Sequence of Operations

```
┌──────────────┐          ┌──────────────────┐
│ API Consumer │          │  url-management   │
└──────┬───────┘          └────────┬──────────┘
       │                           │
       │ POST /api/v1/urls         │
       ├──────────────────────────>│
       │                           │
       │ 201 Created {short_url}   │
       │<──────────────────────────┤
       │                           │
```

---

## Service Interaction Pattern

- **Synchronous**: The entire workflow is synchronous request-response. The API Consumer needs the short URL immediately, and the operation is fast (lookup or insert).
- **Asynchronous**: None — no cross-service communication is needed for this workflow.

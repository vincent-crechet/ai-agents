# Workflow [ID]: [Use Case Title]

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | [Date] | Initial development | Created | — |

**Use Case:** [Link to use case file, e.g., ../../product/use_cases/use_case_XXX_name.md]

---

## Guidance

Workflows document **how services interact** to fulfill a use case — the sequence of service-to-service communication at the business logic level.

**Include:** External actors, services, requests/responses, async events, sequence, data contract references (link to files, don't duplicate)

**Exclude:** Infrastructure (databases, message brokers, caches, load balancers), implementation details (schemas, queries, cache strategies, queue names, algorithms, error codes, performance targets). These belong in service requirements or design documents.

**Async events:** Show service-to-service event flow, not the message broker. Label as `EventName (async)`.

**Length target:** 40-60 lines (not including diagram).

---

## Overview

[1-2 sentences: what this workflow accomplishes and the communication pattern (sync/async/hybrid)]

---

## Participating Services

- **[service-name]**: [One sentence — its role in this workflow]

---

## Sequence of Operations

```
[ASCII diagram showing ONLY: External Actors and Services]

┌──────────┐          ┌─────────────────┐          ┌──────────────┐
│  Client  │          │   Service A     │          │  Service B   │
└────┬─────┘          └────────┬────────┘          └──────┬───────┘
     │                         │                          │
     │ POST /resource          │                          │
     ├────────────────────────>│                          │
     │                         │                          │
     │ 201 Created             │   EventName (async)      │
     │<────────────────────────┤─────────────────────────>│
     │                         │                          │
```

---

## Service Interaction Pattern

- **Synchronous**: [Which interactions are request-response and why]
- **Asynchronous**: [Which interactions are event-driven and why]

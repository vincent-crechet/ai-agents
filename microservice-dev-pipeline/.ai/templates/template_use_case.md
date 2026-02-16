*(Note: consider the product as a whole, do not call out individual services for this use case description)*
# Use Case XXX: [Use Case Title]

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | [Date] | Initial development | Created | — |

## ID
UC-XXX

## Title
[A short, descriptive title for the user journey]

## Actors
- [Primary actors, e.g., End User or the product]
- [Secondary actors or systems, e.g., 3rd party system to integrate with]

## Happy Path
*(Describe the successful, step-by-step, end-to-end user journey)*
1.  Actor A does [Action 1].
2.  The system responds with [Result 1].
3.  Actor A does [Action 2].
4.  The system completes the process with [Final Observable Outcome].

## Acceptance Criteria

**IMPORTANT - User Perspective (Black-Box) Only:**

This section defines what the USER or EXTERNAL OBSERVER can see, experience, or verify.
Write from an external perspective WITHOUT referencing internal implementation details.

**DO include:**
- User-observable outcomes (e.g., "receives a confirmation", "is redirected to the destination")
- User-observable error messages (e.g., "sees an error message indicating invalid input")
- User-observable behavior (e.g., "the page loads", "the action completes")
- Business-level conditions (e.g., "submitting the same input twice produces consistent results")

**DO NOT include:**
- HTTP status codes, database operations, service names, performance metrics, API-level details

**Format:**
- [ ] Given [User Context], when [User Action], then [Observable User Outcome].

**Examples:**

GOOD (User perspective):
- [ ] Given valid input, when the user submits it, then the user receives a result.
- [ ] Given invalid input, when the user submits it, then the user sees a clear error message.

BAD (Implementation details):
- [ ] Given valid input, when the service receives a POST request, then it returns HTTP 200 with JSON.
- [ ] Given a request, when the service processes it, then it publishes an event.

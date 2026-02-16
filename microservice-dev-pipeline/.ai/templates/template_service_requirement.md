# REQ-XXX: [Requirement Title]

## Change History

| Version | Date | Trigger | Description | Downstream Impact |
|---------|------|---------|-------------|-------------------|
| 1.0 | [Date] | Initial development | Created | — |

## ID
REQ-XXX

## Title
[A concise summary of the service's responsibility]

## Parent Use Case
[Link to the source Use Case, e.g., ../../use_cases/uc-XXX.md]

## Requirement
As a **[Service Name]**, I want to **[Perform a specific action]**, so that **[I contribute to a business outcome]**.

## Acceptance Criteria

**IMPORTANT - Service Perspective (Functional WHAT, not Implementation HOW):**

This section defines WHAT the service must do from a functional perspective, focusing on behavior and responsibilities rather than implementation details.

**CRITICAL:** Do NOT repeat the user-level acceptance criteria from the parent use case.
Instead, define WHAT the service is responsible for to implement those user-observable behaviors.

**DO include:**
- API endpoints and their purpose (e.g., "MUST provide a /resources endpoint")
- Input/output data structures (e.g., "MUST accept name field", "MUST return id field")
- Functional behaviors (e.g., "MUST validate input format", "MUST ensure uniqueness")
- Business rules (e.g., "MUST return existing record for duplicate inputs")
- Integration responsibilities (e.g., "MUST publish an event when a resource is created")
- Error conditions and response patterns

**DO NOT include:**
- Database schema details (e.g., table names, column types, indexes)
- Caching strategies and implementation (e.g., Redis keys, TTLs)
- Specific technology choices (e.g., "use PostgreSQL", "use RabbitMQ queue xyz")
- Performance metrics (e.g., "respond within 100ms", "handle 1000 req/sec")
- Implementation algorithms (e.g., "use random alphanumeric generation")
- Generic user-observable outcomes already in parent use case

**Reference Parent Use Case:**
For each criterion, consider: "Which user acceptance criterion does this implement, and WHAT must the service do?"

**Format:**
- [ ] **Given** [Functional precondition], **when** [Service receives input], **then** the service **MUST** [Functional outcome or behavior].
- [ ] **Given** [Edge case], **when** [Action], **then** the service **MUST** [Specific functional behavior].
- [ ] **Given** [Precondition], **when** [Action], **then** [Functional side-effect or responsibility].

**Examples:**

GOOD (Functional WHAT):
- [ ] **Given** valid input, **when** the service receives a create request, **then** it **MUST** return a response containing the created resource.
- [ ] **Given** duplicate input, **when** the service receives the same request, **then** it **MUST** return the existing resource.
- [ ] **Given** a resource is created, **then** the service **MUST** publish a ResourceCreatedEvent.
- [ ] **Given** invalid input, **then** the service **MUST** return an error response.

BAD (Too technical or too vague):
- [ ] **Given** valid input, **then** persist to PostgreSQL table 'items' with columns... (implementation detail)
- [ ] **Given** a request, **then** it responds appropriately. (too vague)
- [ ] **Given** a request, **then** the user sees a result. (user perspective — belongs in use case)
- [ ] **Given** normal operation, **then** respond within 100ms. (performance metric, not functional)

**Structure Guidance:**

For each parent use case acceptance criterion, define service responsibilities covering:
1. **API Contract:** What endpoints exist and what they accept/return (structure, not storage)
2. **Functional Behavior:** What the service does with the data (validate, transform, deduplicate)
3. **Integration Points:** What events/messages the service publishes or consumes (contract, not queue)
4. **Error Handling:** What error conditions the service must recognize and respond to
5. **Business Rules:** What functional constraints or logic the service must enforce
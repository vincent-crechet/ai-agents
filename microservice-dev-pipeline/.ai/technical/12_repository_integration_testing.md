# Repository Integration Testing

Verify that repository adapters actually persist data to the database, not just cache it in the session.

---

## Why These Tests?

Unit tests with in-memory repositories don't catch:
- Missing `commit()` calls (data flushed but not persisted)
- Wrong table/column names (schema mismatches)
- Transaction isolation issues
- Event handler persistence bugs

---

## The Golden Rule: NEW Session Verification

For every write operation, verify persistence with a **different session**:

```python
# 1. Write via repository
await repository.create(name="test")
await session.commit()

# 2. Verify with NEW session (reads from database, not cache)
async with new_session_maker() as fresh:
    result = await fresh.execute(select(Model).where(...))
    assert result is not None  # Fails if commit() was missing!
```

**Why:** Querying with the same session reads from the **session cache**, hiding missing `commit()` bugs. A new session can only read from the **actual database**.

---

## Required Tests

For every service with database persistence:

| Test | What it verifies |
|------|-----------------|
| `test_create_persists` | Create + NEW session read |
| `test_update_persists` | Update + NEW session read |
| `test_delete_persists` | Delete + NEW session read |
| `test_query_returns_persisted_data` | Query via NEW repository instance |
| `test_event_handler_persists` | Only if EVENTS_CONSUMED is not empty |

---

## Template

Use `.ai/templates/template_repository_integration_test.py` for the complete fixture setup and test patterns including:
- Module-scoped testcontainers PostgreSQL container
- Function-scoped async engine with NullPool
- Per-test session and repository fixtures
- NEW session verification examples

---

## Common Pitfalls

| Pitfall | Why it's wrong | Fix |
|---------|---------------|-----|
| Query with same session | Reads from cache, hides missing commit | Use NEW session |
| Rely on `flush()` without `commit()` | Data not persisted to database | Always `commit()` before verification |
| Module-scoped async engine | Event loop conflicts | Use function-scoped async fixtures |
| Missing `NullPool` | Connection pool conflicts in tests | `create_async_engine(url, poolclass=NullPool)` |
| Mock database for repo tests | Defeats the purpose | Use real PostgreSQL via testcontainers |

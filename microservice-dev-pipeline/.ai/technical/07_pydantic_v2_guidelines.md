# Pydantic V2 Guidelines

Breaking changes from V1 and patterns to follow. See `01_architecture_technical_stack.md` for version requirements.

---

## V1 → V2 Quick Reference

### Serialization

| Purpose | V1 | V2 |
|---------|----|----|
| Model → dict | `.dict()` | `.model_dump()` |
| Model → dict (JSON-safe) | `.dict()` | `.model_dump(mode='json')` |
| Model → JSON string | `.json()` | `.model_dump_json()` |
| JSON string → Model | `.parse_raw()` | `.model_validate_json()` |
| ORM → Model | `.from_orm()` | `.model_validate()` |

### Configuration

| Purpose | V1 | V2 |
|---------|----|----|
| ORM initialization | `orm_mode = True` | `from_attributes=True` |
| Immutability | `allow_mutation = False` | `frozen=True` |
| Custom JSON schema | `schema_extra` | `json_schema_extra` |
| Config class | `class Config:` | `model_config = ConfigDict(...)` |
| Settings env file | `class Config: env_file = ".env"` | `model_config = SettingsConfigDict(env_file=".env")` |

### Validation

| Purpose | V1 | V2 |
|---------|----|----|
| Single field | `@validator` | `@field_validator` + `@classmethod` |
| Multiple fields | `@root_validator` | `@model_validator` + `@classmethod` |
| JSON schema | `.schema()` | `.model_json_schema()` |

---

## Critical Pattern: `mode='json'`

When serializing models with datetime, UUID, or Decimal fields for JSON output:

```python
# ❌ TypeError: datetime not JSON serializable
return JSONResponse(content=result.model_dump())

# ✅ Datetimes converted to ISO 8601 strings
return JSONResponse(content=result.model_dump(mode='json'))

# ✅ For message broker payloads
message_body = event.model_dump_json().encode()
```

FastAPI handles this automatically when using `response_model` — manual `mode='json'` is only needed with `JSONResponse`.

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `.dict()` / `.json()` | `AttributeError` | Use `.model_dump()` / `.model_dump_json()` |
| `model_dump()` without `mode='json'` | `TypeError: datetime not serializable` | Add `mode='json'` |
| `.from_orm()` | `AttributeError` | Use `.model_validate()` + `from_attributes=True` |
| `@validator` without `@classmethod` | `TypeError: Validators must be classmethods` | Add `@classmethod` decorator |
| `class Config:` | Deprecated warnings | Use `model_config = ConfigDict(...)` |

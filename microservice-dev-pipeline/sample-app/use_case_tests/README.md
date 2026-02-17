# Use Case Tests

End-to-end tests validating all use cases. Tests are written against the `ITestHarness` protocol and can run in two modes.

## Two Test Modes

### Mock Mode (Default)

Fast, in-memory tests using `MockTestHarness`. No Docker required.

```bash
# From repository root
PYTHONPATH=. python3 -m pytest use_case_tests/ -v
```

### Integration Mode

Tests against real containerized services via Docker Compose. Same test code, different harness.

```bash
# Build images + run tests (recommended)
./use_case_tests/run_integration_tests.sh

# Or step by step:
./use_case_tests/build_test_images.sh
PYTHONPATH=. python3 -m pytest use_case_tests/ --integration -v
```

## Infrastructure

| Container | Host Port | Purpose |
|-----------|-----------|---------|
| url-management | 8001 | URL shortening API |
| analytics | 8002 | Statistics API |
| url-management-db | 5433 | PostgreSQL for url-management |
| analytics-db | 5434 | PostgreSQL for analytics |
| rabbitmq | 5673 / 15673 | Message broker / Management UI |

## Troubleshooting

- **Tests timeout**: Rebuild images with `./use_case_tests/build_test_images.sh`
- **Port conflicts**: Run `docker compose -f use_case_tests/docker-compose.test.yml down`
- **Stale state**: The test harness resets databases between tests automatically

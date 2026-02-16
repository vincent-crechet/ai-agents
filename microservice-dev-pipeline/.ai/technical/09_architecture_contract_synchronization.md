# Architecture Contract Access

How services access contracts from `architecture/contracts/` during development and Docker builds.

---

## Single Source of Truth

Contracts exist only at `architecture/contracts/` (repository root). No copies in service directories.

## During Development

Set PYTHONPATH so services can import contracts:

```bash
PYTHONPATH=/path/to/repo:$PYTHONPATH python -m pytest
```

## During Docker Builds

Build from repository root with `-f` flag so Dockerfiles can access `architecture/`:

```bash
# build_test_images.sh
docker build -f services/<service-name>/Dockerfile -t <service-name>:test .
```

Dockerfiles copy contracts directly:

```dockerfile
COPY services/<service-name>/app/ ./app/
COPY architecture/ ./architecture/
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: 'architecture'` | Verify Dockerfile has `COPY architecture/ ./architecture/`; build from repo root |
| Changes not appearing in container | Rebuild images: `./build_test_images.sh` |
| Docker cache stale | `docker build --no-cache -f services/<service>/Dockerfile .` |

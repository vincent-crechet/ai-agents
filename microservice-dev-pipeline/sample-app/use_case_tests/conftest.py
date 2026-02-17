"""
Pytest configuration for use case tests.

Provides two harness fixtures:
- test_harness: MockTestHarness for fast, in-memory tests (default)
- test_harness: RealServiceHarness for integration tests (with --integration flag)

The --integration flag switches the test_harness fixture to use real services.
"""

import logging
import os
import subprocess
import time

import httpx
import pytest

from use_case_tests.harnesses.mock_harness import MockTestHarness

logger = logging.getLogger(__name__)

COMPOSE_FILE = os.path.join(os.path.dirname(__file__), "docker-compose.test.yml")


def pytest_addoption(parser):
    """Add --integration flag to pytest."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run tests against real containerized services",
    )


def pytest_configure(config):
    """Register the integration marker."""
    config.addinivalue_line(
        "markers", "integration: mark test to run against real services"
    )


def wait_for_service_health(url: str, timeout: int = 90) -> None:
    """Wait until a service health endpoint responds with 200."""
    start = time.time()
    last_error = None
    while time.time() - start < timeout:
        try:
            response = httpx.get(url, timeout=5.0)
            if response.status_code == 200:
                return
        except Exception as e:
            last_error = e
        elapsed = int(time.time() - start)
        if elapsed % 10 == 0 and elapsed > 0:
            logger.info("Still waiting for %s (%ds elapsed)", url, elapsed)
        time.sleep(2)
    raise TimeoutError(
        f"Service at {url} did not become healthy within {timeout}s. "
        f"Last error: {last_error}"
    )


@pytest.fixture(scope="session")
def docker_compose_services(request):
    """
    Start Docker Compose services for integration tests.

    Session-scoped: services start once and stay up for all tests.
    reset() between tests handles isolation.
    """
    if not request.config.getoption("--integration"):
        yield None
        return

    # Clean up any prior crashed runs
    subprocess.run(
        ["docker", "compose", "-f", COMPOSE_FILE, "down", "-v", "--remove-orphans"],
        capture_output=True,
    )

    # Start services
    result = subprocess.run(
        ["docker", "compose", "-f", COMPOSE_FILE, "up", "-d", "--wait"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        # Check if it's a real failure (not just warnings on stderr)
        logger.error("Docker Compose stdout:\n%s", result.stdout)
        logger.error("Docker Compose stderr:\n%s", result.stderr)
        raise RuntimeError(f"Docker Compose up failed (exit code {result.returncode})")

    # Wait for service health
    wait_for_service_health("http://localhost:8001/health")
    wait_for_service_health("http://localhost:8002/health")

    logger.info("All services are healthy")
    yield

    # Teardown
    subprocess.run(
        ["docker", "compose", "-f", COMPOSE_FILE, "down", "-v", "--remove-orphans"],
        capture_output=True,
    )


@pytest.fixture
def test_harness(request, docker_compose_services):
    """
    Provide the appropriate test harness based on the --integration flag.

    Without --integration: returns MockTestHarness (fast, in-memory)
    With --integration: returns RealServiceHarness (real containers via HTTP)
    """
    if request.config.getoption("--integration"):
        from use_case_tests.harnesses.real_service_harness import RealServiceHarness

        harness = RealServiceHarness(
            url_management_url="http://localhost:8001",
            analytics_url="http://localhost:8002",
            url_management_db_url="postgresql+psycopg2://postgres:postgres@localhost:5433/url_management",
            analytics_db_url="postgresql+psycopg2://postgres:postgres@localhost:5434/analytics",
            rabbitmq_management_url="http://localhost:15673",
        )
        harness.reset()
        yield harness
        harness.close()
    else:
        yield MockTestHarness()

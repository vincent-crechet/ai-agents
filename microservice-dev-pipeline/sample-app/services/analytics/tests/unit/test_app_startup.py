"""
Tests for FastAPI application startup.

Verifies that the app can be imported and has expected routes.
"""

from app.main import app


def test_app_can_be_imported() -> None:
    """The FastAPI app should be importable without errors."""
    assert app is not None
    assert app.title == "Analytics Service"


def test_app_has_health_route() -> None:
    """The app should have a /health endpoint."""
    routes = [route.path for route in app.routes]
    assert "/health" in routes


def test_app_has_stats_top_route() -> None:
    """The app should have a /api/v1/stats/top endpoint."""
    routes = [route.path for route in app.routes]
    assert "/api/v1/stats/top" in routes

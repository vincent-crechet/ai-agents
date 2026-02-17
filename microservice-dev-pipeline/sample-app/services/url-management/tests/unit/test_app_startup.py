"""
Tests for FastAPI application startup and configuration.

Verifies that the application can be imported and has the expected routes.
"""

from app.main import app


def test_app_has_health_endpoint() -> None:
    """Test that the health endpoint is registered."""
    routes = [route.path for route in app.routes]
    assert "/health" in routes


def test_app_has_shorten_endpoint() -> None:
    """Test that the URL shortening endpoint is registered."""
    routes = [route.path for route in app.routes]
    assert "/api/v1/urls" in routes


def test_app_has_redirect_endpoint() -> None:
    """Test that the redirect endpoint is registered."""
    routes = [route.path for route in app.routes]
    assert "/{short_code}" in routes


def test_app_title() -> None:
    """Test that the app has the correct title."""
    assert app.title == "URL Management Service"

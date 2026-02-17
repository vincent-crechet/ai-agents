"""
Configuration settings for the url-management service.

Uses pydantic-settings to load configuration from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/url_management"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "url_shortener"
    base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env")


def get_settings() -> Settings:
    """Return application settings instance."""
    return Settings()

"""
Configuration settings for the analytics service.

Uses pydantic-settings for environment-aware configuration.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Analytics service configuration loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/analytics"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "url_shortener"
    service_name: str = "analytics"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

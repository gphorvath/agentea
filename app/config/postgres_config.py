"""Postgres configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    """Postgres settings for the application."""

    model_config = SettingsConfigDict(env_prefix="AGENTEA_POSTGRES_")

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "agentea"

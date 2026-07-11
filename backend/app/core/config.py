"""Application configuration, loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database (psycopg v3 driver)
    database_url: str = (
        "postgresql+psycopg://footpass:footpass@footpass-db:5432/footpass"
    )

    # Storage
    footpass_data_dir: str = "/data"

    # App metadata
    footpass_version: str = "0.1.0"
    footpass_env: str = "production"
    footpass_hostname: str = "footpass.local"

    # Security
    footpass_secret_key: str = "dev-insecure-change-me"

    # Vision / AI review (local network MedGemma node). "none" disables it.
    footpass_vision_provider: str = "none"  # none | remote_local_network | local_gpu
    footpass_vision_endpoint: str = "http://192.168.0.79:11434"
    footpass_vision_model: str = "footpass-medgemma"
    footpass_vision_timeout: int = 240

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_dev(self) -> bool:
        return self.footpass_env.lower() in {"dev", "development", "local"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

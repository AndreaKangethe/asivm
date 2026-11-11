from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./asivm.db"
    scan_interval_minutes: int = 60
    model_artifact_path: str = "backend/ml/artifacts"
    api_key: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

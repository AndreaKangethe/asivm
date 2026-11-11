from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./asivm.db"
    scan_interval_seconds: int = 3600
    infer_interval_seconds: int = 300
    model_artifact_path: str = "ml/artifacts"
    feature_version: str = "v1"
    log_level: str = "INFO"
    api_key: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def scan_interval_minutes(self) -> float:
        return self.scan_interval_seconds / 60


@lru_cache
def get_settings() -> Settings:
    return Settings()

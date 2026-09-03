"""Application settings loaded from environment / .env file."""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    max_upload_bytes: int = 52428800  # 50 MB
    allowed_extensions: List[str] = [".tif", ".tiff", ".png", ".jpg", ".jpeg"]

    runtime_dir: Path = Path("runtime")
    job_timeout_seconds: int = 300
    max_concurrent_jobs: int = 1

    SATQUERY_MODEL_MODE: str = "mock"

    @property
    def assets_dir(self) -> Path:
        return self.runtime_dir / "assets"

    @property
    def jobs_dir(self) -> Path:
        return self.runtime_dir / "jobs"


settings = Settings()

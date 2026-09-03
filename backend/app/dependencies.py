"""FastAPI Depends() providers. Singletons live on app.state and are exposed here
so route handlers stay thin and testable."""
from fastapi import Request

from app.config import Settings, settings as _settings
from app.services.asset_service import AssetStore
from app.services.job_service import JobStore
from app.workers.job_worker import JobWorker


def get_settings() -> Settings:
    return _settings


def get_asset_store(request: Request) -> AssetStore:
    return request.app.state.asset_store


def get_job_store(request: Request) -> JobStore:
    return request.app.state.job_store


def get_job_worker(request: Request) -> JobWorker:
    return request.app.state.job_worker

"""FastAPI application entry point.

Run from the `backend/` directory:      uvicorn app.main:app --reload
or from the repo root (this file adds `backend/` to sys.path so the
`from app.xxx import ...` style imports used throughout resolve either way):
                                          uvicorn backend.app.main:app --reload
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assets import router as assets_router
from app.api.errors import register_error_handlers
from app.api.jobs import router as jobs_router
from app.api.system import router as system_router
from app.config import settings
from app.services.asset_service import AssetStore
from app.services.job_service import JobStore
from app.storage.filesystem import ensure_dir
from app.workers.job_worker import JobWorker

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("satquery.main")

app = FastAPI(
    title="SatQuery AI Backend API",
    description="Adapter layer for SatQuery Engine V1.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

register_error_handlers(app)

app.include_router(assets_router)
app.include_router(jobs_router)
app.include_router(system_router)


@app.on_event("startup")
def on_startup():
    ensure_dir(settings.runtime_dir)
    ensure_dir(settings.assets_dir)
    ensure_dir(settings.jobs_dir)
    app.state.asset_store = AssetStore(settings)
    app.state.job_store = JobStore(settings.jobs_dir)
    app.state.job_worker = JobWorker(max_workers=settings.max_concurrent_jobs)
    logger.info("SatQuery backend started. model_mode=%s runtime_dir=%s", settings.SATQUERY_MODEL_MODE, settings.runtime_dir)


@app.on_event("shutdown")
def on_shutdown():
    app.state.job_worker.shutdown(wait=False)

"""Serves evidence files (PNG previews/masks/visualizations) written by the engine
into runtime/jobs/{job_id}/output/. Path-traversal-safe by construction."""
from pathlib import Path

from app.services.asset_service import ApiError
from app.storage.paths import is_safe_evidence_filename


def resolve_evidence_path(jobs_dir: Path, job_id: str, filename: str) -> Path:
    if not is_safe_evidence_filename(filename):
        raise ApiError("INVALID_FILENAME", 400, "Filename contains illegal characters or path traversal")

    evidence_dir = (jobs_dir / job_id / "output").resolve()
    file_path = (evidence_dir / filename).resolve()

    if not file_path.is_relative_to(evidence_dir):
        raise ApiError("INVALID_FILENAME", 400, "Resolved path escapes the job's evidence directory")

    if not file_path.exists():
        raise ApiError("EVIDENCE_NOT_FOUND", 404, f"No evidence file named {filename!r}")

    return file_path

"""In-memory + filesystem job store. No database (see SRS section 23)."""
import dataclasses
import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.storage.filesystem import ensure_dir


@dataclasses.dataclass
class JobRecord:
    job_id: str
    status: str  # queued | running | completed | failed | cancelled
    query: str
    asset_refs: list
    created_at: str
    updated_at: str
    result: Optional[dict] = None
    error_message: Optional[str] = None
    engine_request_id: Optional[str] = None


class JobStore:
    def __init__(self, jobs_dir: Path):
        self._jobs: dict[str, JobRecord] = {}
        self._jobs_dir = jobs_dir
        self._lock = threading.Lock()
        ensure_dir(jobs_dir)

    def new_job_id(self) -> str:
        return str(uuid.uuid4())

    def create(self, record: JobRecord) -> JobRecord:
        with self._lock:
            self._jobs[record.job_id] = record
            self._persist(record)
        return record

    def update(self, job_id: str, **kwargs) -> JobRecord:
        with self._lock:
            record = self._jobs[job_id]
            for k, v in kwargs.items():
                setattr(record, k, v)
            record.updated_at = datetime.now(timezone.utc).isoformat()
            self._persist(record)
            return record

    def get(self, job_id: str) -> Optional[JobRecord]:
        return self._jobs.get(job_id)

    def _persist(self, record: JobRecord) -> None:
        job_dir = self._jobs_dir / record.job_id
        ensure_dir(job_dir)
        (job_dir / "job.json").write_text(json.dumps(dataclasses.asdict(record), default=str))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

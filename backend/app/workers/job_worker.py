"""Single-worker ThreadPoolExecutor. max_workers=1 by design: engine inference
must never run concurrently on a low-spec, GPU-optional laptop (SRS section 24)."""
import threading
from concurrent.futures import ThreadPoolExecutor


class JobWorker:
    def __init__(self, max_workers: int = 1):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._active_jobs: set[str] = set()
        self._lock = threading.Lock()

    def submit(self, job_id: str, fn, *args):
        return self._executor.submit(self._run, job_id, fn, *args)

    def _run(self, job_id: str, fn, *args):
        with self._lock:
            self._active_jobs.add(job_id)
        try:
            fn(*args)
        finally:
            with self._lock:
                self._active_jobs.discard(job_id)

    def is_active(self, job_id: str) -> bool:
        with self._lock:
            return job_id in self._active_jobs

    def shutdown(self, wait: bool = False):
        self._executor.shutdown(wait=wait)

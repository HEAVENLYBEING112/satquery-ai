"""Assembles the downloadable report for a completed job.

Per SRS 16.7: the report body is the exact EngineResultResponse JSON already
stored on the job record — no fabricated fields are ever added.
"""
from app.services.asset_service import ApiError


def build_report(job_record) -> dict:
    if job_record.status not in ("completed", "failed"):
        raise ApiError("JOB_NOT_COMPLETE", 409, "Job has not finished yet")
    if job_record.result is None:
        raise ApiError("JOB_NOT_COMPLETE", 409, "Job has no result to report")
    return job_record.result

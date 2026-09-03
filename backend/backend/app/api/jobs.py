from fastapi import APIRouter, Depends

from app.dependencies import get_asset_store, get_job_store, get_job_worker, get_settings
from app.schemas.engine import EngineResultResponse
from app.schemas.errors import ApiErrorSchema
from app.schemas.jobs import JobResponse, JobSubmitRequest
from app.services.asset_service import ApiError, AssetStore
from app.services.engine_service import invoke_engine, is_engine_available
from app.services.evidence_service import resolve_evidence_path
from app.services.job_service import JobRecord, JobStore, now_iso
from app.services.report_service import build_report
from app.workers.job_worker import JobWorker
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/api/v1", tags=["jobs"])

NOT_FOUND_RESPONSE = {404: {"model": ApiErrorSchema, "description": "JOB_NOT_FOUND — unknown job_id."}}
NOT_COMPLETE_RESPONSE = {409: {"model": ApiErrorSchema, "description": "JOB_NOT_COMPLETE — job has not finished."}}


@router.post(
    "/jobs",
    response_model=JobResponse,
    status_code=202,
    responses={
        400: {"model": ApiErrorSchema, "description": "INVALID_REQUEST — malformed asset/modality combination."},
        404: {"model": ApiErrorSchema, "description": "ASSET_NOT_FOUND — one of the referenced asset_ids does not exist."},
        422: {"model": ApiErrorSchema, "description": "VALIDATION_ERROR — request failed schema validation."},
        503: {"model": ApiErrorSchema, "description": "ENGINE_UNAVAILABLE — `from engine import SatQueryEngine` failed."},
    },
    summary="Submit an analysis job",
)
def submit_job(
    request: JobSubmitRequest,
    asset_store: AssetStore = Depends(get_asset_store),
    job_store: JobStore = Depends(get_job_store),
    job_worker: JobWorker = Depends(get_job_worker),
    settings=Depends(get_settings),
):
    if not is_engine_available():
        raise ApiError("ENGINE_UNAVAILABLE", 503, "Engine V1 is not importable on this server.")

    for asset_ref in request.assets:
        if not asset_store.get(asset_ref.asset_id):
            raise ApiError("ASSET_NOT_FOUND", 404, f"Asset {asset_ref.asset_id} does not exist.")

    job_id = job_store.new_job_id()
    created_at = now_iso()
    record = JobRecord(
        job_id=job_id,
        status="queued",
        query=request.query,
        asset_refs=[a.model_dump() for a in request.assets],
        created_at=created_at,
        updated_at=created_at,
    )
    job_store.create(record)

    job_worker.submit(job_id, invoke_engine, job_id, request, asset_store, job_store, settings)

    return JobResponse(job_id=job_id, status="queued", created_at=created_at)


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    responses=NOT_FOUND_RESPONSE,
    summary="Poll job status",
)
def get_job(job_id: str, job_store: JobStore = Depends(get_job_store)):
    record = job_store.get(job_id)
    if not record:
        raise ApiError("JOB_NOT_FOUND", 404, f"Job {job_id} does not exist.")
    return JobResponse(
        job_id=record.job_id,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        result=record.result,
    )


@router.get(
    "/jobs/{job_id}/trace",
    responses={**NOT_FOUND_RESPONSE, **NOT_COMPLETE_RESPONSE},
    summary="Get the execution trace for a completed job",
)
def get_trace(job_id: str, job_store: JobStore = Depends(get_job_store)):
    record = job_store.get(job_id)
    if not record:
        raise ApiError("JOB_NOT_FOUND", 404, f"Job {job_id} does not exist.")
    if record.status not in ("completed", "failed"):
        raise ApiError("JOB_NOT_COMPLETE", 409, "Job has not finished yet.")
    trace = (record.result or {}).get("execution_trace", [])
    return JSONResponse(content={"job_id": job_id, "trace": trace})


@router.get(
    "/jobs/{job_id}/evidence/{filename}",
    responses={
        400: {"model": ApiErrorSchema, "description": "INVALID_FILENAME — path traversal or illegal characters."},
        404: {"model": ApiErrorSchema, "description": "JOB_NOT_FOUND or EVIDENCE_NOT_FOUND."},
        200: {"content": {"image/png": {}}, "description": "PNG evidence file."},
    },
    summary="Fetch an evidence file (visualization or change mask) for a job",
)
def get_evidence(job_id: str, filename: str, job_store: JobStore = Depends(get_job_store), settings=Depends(get_settings)):
    if not job_store.get(job_id):
        raise ApiError("JOB_NOT_FOUND", 404, f"Job {job_id} does not exist.")
    file_path = resolve_evidence_path(settings.jobs_dir, job_id, filename)
    return FileResponse(str(file_path), media_type="image/png")


@router.get(
    "/jobs/{job_id}/report",
    response_model=EngineResultResponse,
    responses={**NOT_FOUND_RESPONSE, **NOT_COMPLETE_RESPONSE},
    summary="Download the full EngineResult report for a completed job",
)
def get_report(job_id: str, job_store: JobStore = Depends(get_job_store)):
    record = job_store.get(job_id)
    if not record:
        raise ApiError("JOB_NOT_FOUND", 404, f"Job {job_id} does not exist.")
    report = build_report(record)
    headers = {"Content-Disposition": f"attachment; filename=satquery_report_{job_id}.json"}
    return JSONResponse(content=report, headers=headers)

"""Converts engine dataclasses (engine/contracts.py) into API Pydantic schemas.

This is the most critical module in the backend: it is the only place that
touches the raw engine output, so every "never coerce" / "never fabricate"
rule in the SRS is enforced here.
"""
from pathlib import Path
from typing import Any

from app.schemas.engine import (
    BoundingBoxResponse,
    ChangeMaskResponse,
    EngineErrorResponse,
    EngineResultResponse,
    EvidenceBundleResponse,
    SpecialistResultResponse,
    TraceStepResponse,
)


def path_to_evidence_url(path: str, job_id: str, job_output_dir: Path) -> str:
    file_path = Path(path)
    job_output_dir = job_output_dir.resolve()
    resolved = file_path.resolve()
    if not resolved.is_relative_to(job_output_dir):
        raise ValueError("Evidence path outside allowed job output directory")
    return f"/api/v1/jobs/{job_id}/evidence/{resolved.name}"


def determine_coordinate_type(bb, asset_map: dict) -> str:
    """OpticalSARSpecialist always produces pixel coords. CROMA produces
    geographic coordinates only when the source asset carries a CRS + bbox."""
    if getattr(bb, "source", None) == "croma_classifier":
        for asset in asset_map.values():
            if getattr(asset, "crs", None) and getattr(asset, "bbox", None):
                return "geo"
    return "pixel"


def sanitize_trace_step(ts: dict) -> dict:
    summary = ts.get("result_summary")
    if isinstance(summary, str) and ("/" in summary or "\\" in summary):
        summary = "[redacted]"
    return {**ts, "result_summary": summary}


def serialize_bounding_box(bb, asset_map: dict) -> BoundingBoxResponse:
    return BoundingBoxResponse(
        label=bb.label,
        coordinates=list(bb.coordinates),
        coordinate_type=determine_coordinate_type(bb, asset_map),
        confidence=bb.confidence,  # preserve null, never coerce
        source=bb.source,
    )


def serialize_evidence_bundle(bundle, job_id: str, asset_map: dict, job_output_dir: Path) -> EvidenceBundleResponse:
    vis_urls = [path_to_evidence_url(p, job_id, job_output_dir) for p in (bundle.visualizations or []) if p]

    change_mask_resp = None
    if bundle.change_mask:
        mask_url = None
        if bundle.change_mask.mask_path:
            mask_url = path_to_evidence_url(bundle.change_mask.mask_path, job_id, job_output_dir)
        change_mask_resp = ChangeMaskResponse(
            width=bundle.change_mask.width,
            height=bundle.change_mask.height,
            mask_url=mask_url,
            threshold_used=bundle.change_mask.threshold_used,
            changed_pixel_count=bundle.change_mask.changed_pixel_count,
            changed_fraction=bundle.change_mask.changed_fraction,
        )

    return EvidenceBundleResponse(
        textual_evidence=bundle.textual_evidence,
        bounding_boxes=[serialize_bounding_box(bb, asset_map) for bb in (bundle.bounding_boxes or [])],
        visualizations=vis_urls,
        change_statistics=bundle.change_statistics,
        change_mask=change_mask_resp,
        metadata=bundle.metadata or {},  # preserve fallback_triggered / fallback_reason verbatim
    )


def serialize_specialist_result(sr, job_id: str, asset_map: dict, job_output_dir: Path) -> SpecialistResultResponse:
    task_value = sr.task.value if hasattr(sr.task, "value") else sr.task
    return SpecialistResultResponse(
        status=sr.status,
        model_name=sr.model_name,
        task=task_value,
        answer=str(sr.answer) if sr.answer is not None else None,
        confidence=sr.confidence,  # NULLABLE — never coerce
        evidence=serialize_evidence_bundle(sr.evidence, job_id, asset_map, job_output_dir),
        metadata=sr.metadata or {},
        execution_time=sr.execution_time,
        error=sr.error,
    )


def serialize_engine_result(result, job_id: str, asset_map: dict, job_output_dir: Path) -> EngineResultResponse:
    # Known engine bug: errors field defaults to {} via field(default_factory=dict)
    # on success instead of []. Coerce defensively.
    errors_raw = result.errors
    if isinstance(errors_raw, dict):
        errors: list[EngineErrorResponse] = []
    elif isinstance(errors_raw, list):
        errors = [EngineErrorResponse(code=e.code, message=e.message) for e in errors_raw]
    else:
        errors = []

    return EngineResultResponse(
        request_id=result.request_id,
        status=result.status,
        query=result.query,
        task=result.task.value if getattr(result, "task", None) else None,
        answer=str(result.answer) if result.answer is not None else None,
        confidence=result.confidence,  # preserve null — NEVER substitute a default
        specialist_results=[
            serialize_specialist_result(sr, job_id, asset_map, job_output_dir) for sr in result.specialist_results
        ],
        evidence=[serialize_evidence_bundle(eb, job_id, asset_map, job_output_dir) for eb in result.evidence],
        execution_trace=[TraceStepResponse(**sanitize_trace_step(ts)) for ts in result.execution_trace],
        errors=errors,
    )

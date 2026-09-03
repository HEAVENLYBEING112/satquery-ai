"""Tests for the engine result serializer using lightweight fakes that mimic
engine/contracts.py dataclasses, so these tests never need the real engine."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from app.serializers.engine_result import (
    determine_coordinate_type,
    serialize_engine_result,
)


@dataclass
class FakeBoundingBox:
    label: str
    coordinates: list
    confidence: Optional[float]
    source: str


@dataclass
class FakeChangeMask:
    width: int
    height: int
    mask_path: Optional[str]
    threshold_used: Optional[float]
    changed_pixel_count: int
    changed_fraction: float


@dataclass
class FakeEvidenceBundle:
    textual_evidence: Optional[str] = None
    bounding_boxes: list = field(default_factory=list)
    visualizations: list = field(default_factory=list)
    change_statistics: Optional[dict] = None
    change_mask: Optional[FakeChangeMask] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class FakeSpecialistResult:
    status: str
    model_name: str
    task: Any
    answer: Any
    confidence: Optional[float]
    evidence: FakeEvidenceBundle
    metadata: dict
    execution_time: float
    error: Optional[str] = None


@dataclass
class FakeEngineError:
    code: str
    message: str


@dataclass
class FakeEngineResult:
    request_id: str
    status: str
    query: str
    task: Any
    answer: Any
    confidence: Optional[float]
    specialist_results: list
    evidence: list
    execution_trace: list
    errors: Any


@dataclass
class FakeAsset:
    crs: Optional[str] = None
    bbox: Optional[list] = None


def _bundle_with_output_dir(tmp_path):
    output_dir = tmp_path / "jobs" / "job1" / "output"
    output_dir.mkdir(parents=True)
    return output_dir


def test_confidence_none_preserved(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    result = FakeEngineResult(
        request_id="r1", status="success", query="q", task=None, answer=None,
        confidence=None, specialist_results=[], evidence=[], execution_trace=[], errors={},
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert serialized.confidence is None


def test_confidence_float_preserved(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    result = FakeEngineResult(
        request_id="r1", status="success", query="q", task=None, answer=None,
        confidence=0.87, specialist_results=[], evidence=[], execution_trace=[], errors=[],
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert serialized.confidence == 0.87


def test_errors_dict_coerced_to_list(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    result = FakeEngineResult(
        request_id="r1", status="success", query="q", task=None, answer=None,
        confidence=None, specialist_results=[], evidence=[], execution_trace=[], errors={},
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert serialized.errors == []


def test_errors_list_passed_through(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    result = FakeEngineResult(
        request_id="r1", status="failed", query="q", task=None, answer=None,
        confidence=None, specialist_results=[], evidence=[], execution_trace=[],
        errors=[FakeEngineError(code="PLANNING_FAILED", message="no route")],
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert len(serialized.errors) == 1
    assert serialized.errors[0].code == "PLANNING_FAILED"


def test_fallback_metadata_passthrough(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    bundle = FakeEvidenceBundle(metadata={"fallback_triggered": True, "fallback_reason": "CROMA unavailable"})
    sr = FakeSpecialistResult(
        status="success", model_name="OpticalSARSpecialist", task="cross_modal_optical_sar",
        answer="answer", confidence=None, evidence=bundle, metadata={}, execution_time=1.2,
    )
    result = FakeEngineResult(
        request_id="r1", status="success", query="q", task=None, answer=None,
        confidence=None, specialist_results=[sr], evidence=[bundle], execution_trace=[], errors=[],
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert serialized.evidence[0].metadata["fallback_triggered"] is True
    assert serialized.evidence[0].metadata["fallback_reason"] == "CROMA unavailable"


def test_bounding_box_confidence_none_preserved(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    bb = FakeBoundingBox(label="water", coordinates=[0, 0, 10, 10], confidence=None, source="optical")
    bundle = FakeEvidenceBundle(bounding_boxes=[bb])
    result = FakeEngineResult(
        request_id="r1", status="success", query="q", task=None, answer=None,
        confidence=None, specialist_results=[], evidence=[bundle], execution_trace=[], errors=[],
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert serialized.evidence[0].bounding_boxes[0].confidence is None
    assert serialized.evidence[0].bounding_boxes[0].coordinate_type == "pixel"


def test_coordinate_type_optical_is_pixel():
    bb = FakeBoundingBox(label="x", coordinates=[0, 0, 1, 1], confidence=None, source="optical")
    assert determine_coordinate_type(bb, {}) == "pixel"


def test_coordinate_type_croma_with_crs_is_geo():
    bb = FakeBoundingBox(label="x", coordinates=[0, 0, 1, 1], confidence=None, source="croma_classifier")
    asset_map = {"a1": FakeAsset(crs="EPSG:4326", bbox=[0, 0, 1, 1])}
    assert determine_coordinate_type(bb, asset_map) == "geo"


def test_coordinate_type_croma_without_crs_is_pixel():
    bb = FakeBoundingBox(label="x", coordinates=[0, 0, 1, 1], confidence=None, source="croma_classifier")
    asset_map = {"a1": FakeAsset(crs=None, bbox=None)}
    assert determine_coordinate_type(bb, asset_map) == "pixel"


def test_trace_step_redacts_server_path(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    trace = [{
        "step": 1, "tool": "baseline_change_detector", "task": "temporal_change_detection",
        "status": "success", "parameters": {}, "duration_ms": 100,
        "result_summary": "/home/user/runtime/jobs/job1/output/mask.png",
    }]
    result = FakeEngineResult(
        request_id="r1", status="success", query="q", task=None, answer=None,
        confidence=None, specialist_results=[], evidence=[], execution_trace=trace, errors=[],
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert serialized.execution_trace[0].result_summary == "[redacted]"


def test_visualization_path_rewritten_to_url(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    vis_file = output_dir / "vis1.png"
    vis_file.write_bytes(b"fake")
    bundle = FakeEvidenceBundle(visualizations=[str(vis_file)])
    result = FakeEngineResult(
        request_id="r1", status="success", query="q", task=None, answer=None,
        confidence=None, specialist_results=[], evidence=[bundle], execution_trace=[], errors=[],
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert serialized.evidence[0].visualizations == ["/api/v1/jobs/job1/evidence/vis1.png"]


def test_mask_path_rewritten_and_null_stays_null(tmp_path):
    output_dir = _bundle_with_output_dir(tmp_path)
    mask_file = output_dir / "mask.png"
    mask_file.write_bytes(b"fake")

    bundle_with_mask = FakeEvidenceBundle(
        change_mask=FakeChangeMask(width=10, height=10, mask_path=str(mask_file), threshold_used=0.5, changed_pixel_count=5, changed_fraction=0.05)
    )
    bundle_without_mask_path = FakeEvidenceBundle(
        change_mask=FakeChangeMask(width=10, height=10, mask_path=None, threshold_used=None, changed_pixel_count=0, changed_fraction=0.0)
    )
    result = FakeEngineResult(
        request_id="r1", status="success", query="q", task=None, answer=None,
        confidence=None, specialist_results=[], evidence=[bundle_with_mask, bundle_without_mask_path],
        execution_trace=[], errors=[],
    )
    serialized = serialize_engine_result(result, "job1", {}, output_dir)
    assert serialized.evidence[0].change_mask.mask_url == "/api/v1/jobs/job1/evidence/mask.png"
    assert serialized.evidence[1].change_mask.mask_url is None

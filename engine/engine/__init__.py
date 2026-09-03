"""
*** DEV-ONLY STUB — NOT ENGINE V1 ***
Minimal SatQueryEngine implementation so the backend has something real to
call while origin/feat/engine-core isn't checked out yet. Always runs in
"mock" fashion and always routes to a trivial VQA/change-detection/CROMA-
fallback response, just enough to exercise every backend code path
(serialization, evidence URLs, fallback metadata, nullable confidence, etc).

Replace this entire directory with the real engine before doing anything
that depends on actual model output quality.
"""
import time
import uuid
from pathlib import Path

from engine.contracts import (
    BoundingBox,
    ChangeMask,
    EngineResult,
    EvidenceBundle,
    SpecialistResult,
    TaskType,
)


def _write_placeholder_png(path: Path) -> None:
    # 1x1 transparent PNG, just enough for evidence-serving to have a real file.
    png_bytes = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
        "de0000000a49444154789c6360000002000155035a300000000049454e44ae42"
        "6082"
    )
    path.write_bytes(png_bytes)


class SatQueryEngine:
    def __init__(self, registry=None):
        self.registry = registry

    def analyze(self, bundle, query: str) -> EngineResult:
        import os

        request_id = str(uuid.uuid4())
        output_dir = Path(os.environ.get("SATQUERY_OUTPUT_DIR", "outputs"))
        output_dir.mkdir(parents=True, exist_ok=True)

        start = time.time()

        if bundle.is_cross_modal:
            task = TaskType.CROSS_MODAL_OPTICAL_SAR
            model_name = "optical_sar_specialist"
            fallback = {
                "fallback_triggered": True,
                "fallback_reason": "CROMA hardware/dependencies unavailable",
            }
            confidence = None
            answer = "Cross-modal analysis completed via fallback specialist."
        elif bundle.is_temporal:
            task = TaskType.TEMPORAL_CHANGE_DETECTION
            model_name = "baseline_change_detector"
            fallback = {}
            confidence = 0.72
            answer = "3 changed regions detected between the two acquisitions."
        else:
            task = TaskType.SINGLE_IMAGE_VQA
            model_name = "MockVQA"
            fallback = {}
            confidence = 0.91
            answer = f"Mock answer for query: {query!r}"

        vis_path = output_dir / f"{request_id}_vis.png"
        _write_placeholder_png(vis_path)

        bbox = BoundingBox(label="region_of_interest", coordinates=[10, 10, 100, 100], confidence=confidence, source=model_name if task != TaskType.CROSS_MODAL_OPTICAL_SAR else "optical")

        evidence = EvidenceBundle(
            textual_evidence=answer,
            bounding_boxes=[bbox],
            visualizations=[str(vis_path)],
            change_statistics={"changed_fraction": 0.05} if task == TaskType.TEMPORAL_CHANGE_DETECTION else None,
            change_mask=None,
            metadata=fallback,
        )

        duration_ms = int((time.time() - start) * 1000)

        specialist_result = SpecialistResult(
            status="success",
            model_name=model_name,
            task=task,
            answer=answer,
            confidence=confidence,
            evidence=evidence,
            metadata={},
            execution_time=time.time() - start,
        )

        trace = [{
            "step": 1,
            "tool": model_name,
            "task": task.value,
            "status": "success",
            "parameters": {},
            "duration_ms": duration_ms,
            "result_summary": answer,
        }]

        return EngineResult(
            request_id=request_id,
            status="success",
            query=query,
            task=task,
            answer=answer,
            confidence=confidence,
            specialist_results=[specialist_result],
            evidence=[evidence],
            execution_trace=trace,
            errors={},  # reproduces documented bug; backend serializer must coerce to []
        )

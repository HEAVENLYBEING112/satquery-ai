# SatQuery AI Engine V1 — Frozen Baseline

ENGINE V1 IS FROZEN.

The engine should only be modified if integration exposes a genuine contract defect or a critical correctness/security issue.

## 1. Freeze Status
- **Status:** FROZEN
- **Freeze Date:** 2026-09-01
- **Git Branch:** `feat/engine-core`
- **Git Commit:** `b4b8567`
- **Test Status:** 41 passed, 1 skipped, 0 failures, 0 errors

## 2. Public Entrypoint
The primary entrypoint for the engine is:
```python
from engine.core import SatQueryEngine
engine = SatQueryEngine()
result = engine.analyze(inputs=input_bundle, query=query)
```
Backend must treat the engine as a black-box service/library. 

## 3. Input Contract
The engine expects an `InputBundle` consisting of `ImageAsset` objects.
```python
from engine.contracts import InputBundle, ImageAsset
```

## 4. Output Contract
The engine returns an `EngineResult` containing:
- `request_id`: The ID of the execution.
- `status`: Execution status ("success" or "error").
- `query`: The initial string query.
- `task`: The identified `TaskType`.
- `answer`: The semantic text/dict answer.
- `confidence`: Mathematical confidence (or `None`).
- `specialist_results`: Array of `SpecialistResult`.
- `evidence`: Array of `EvidenceBundle`.
- `execution_trace`: Dictionary list tracing engine steps.

## 5. Supported Workflows
The following workflows are supported in V1:
- `SINGLE_IMAGE_VQA` (Real / Mock fallback)
- `SINGLE_IMAGE_CAPTION` (Real / Mock fallback)
- `SINGLE_IMAGE_GROUNDING` (Real / Mock fallback)
- `TEMPORAL_CHANGE_DETECTION` (Deterministic Baseline)
- `TEMPORAL_CHANGE_DESCRIPTION` (Deterministic Baseline)
- `TEMPORAL_CHANGE_VQA` (Mock)
- `CROSS_MODAL_OPTICAL_SAR` (Deterministic Baseline)
- `CROMA_CLASSIFICATION` (Real / Deterministic fallback)

Note: Do NOT claim a workflow is fully AI-powered if it currently relies on deterministic fallback or mock behavior.

## 6. Specialist Architecture
The backend must NOT depend on:
- Internal specialist implementation
- Internal model-loading logic
- Private helper methods
- Internal planner rules
- Implementation-specific Python classes unless explicitly public

## 7. Confidence Semantics
The engine MUST NOT fabricate confidence values.
- `None` means no scientifically justified probability/confidence was produced.
- Mock models do not report arbitrary confidence. They return `None`.
- Deterministic outputs do not automatically get converted into fake probability percentages.
- Real model confidence is only reported when the underlying model mathematically provides an interpretable probability measure.
- Dataset accuracy metrics are NOT per-query confidence values.

## 8. Fallback Behavior
Fallback mechanism is strict and observable.
Example Flow:
1. CROMA / heavyweight model unavailable
2. engine catches supported failure
3. fallback triggered
4. deterministic `OpticalSARSpecialist` executes
5. `EvidenceBundle` created
6. `EngineResult` returned

Fallback remains strictly observable in the execution trace and evidence metadata (via `fallback_triggered: True`). The engine never silently pretends the AI model executed.

## 9. Evidence Model
The `EvidenceBundle` provides verifiable facts backing the `answer`:
- `textual_evidence`
- `bounding_boxes`
- `visualizations`
- `change_statistics`
- `change_mask`
- `metadata`

## 10. Execution Trace
The `execution_trace` provides an internal developer-oriented timeline of the planner and tools used.

## 11. Low-Spec Guarantee
The development environment does NOT require:
- GPU
- CROMA weights
- GeoChat weights
- BigEarthNet-MM full dataset
- heavyweight model inference

Core deterministic workflows and tests remain runnable on the low-spec development machine via mock and baseline execution paths.

## 12. Known Limitations
- Real GeoChat inference requires suitable hardware/dependencies.
- CROMA downstream classifier training/evaluation requires GPU/data environment.
- Synthetic fixtures are used for many local tests.
- Public benchmark evaluation is separate from engine unit testing.
- Tile-level classification does not inherently provide pixel-level segmentation.
- Mock workflows are for development/testing only.
- Real-world benchmark metrics have not been fabricated.

## 13. Backend Integration Rules
Backend developers must integrate strictly against the `SatQueryEngine.analyze()` interface and explicitly provided contract data structures.

## 14. Frontend Integration Rules
Frontend developers map `EngineResult` properties directly to the UI, explicitly recognizing `fallback_triggered` flags and absent `confidence` values.

## 15. Engine V1 Freeze Policy
Rules:
1. `feat/engine-core` is frozen.
2. Backend and frontend development must integrate against the existing public contract.
3. Developers must not modify engine internals to accommodate normal frontend/backend implementation preferences.
4. Contract changes require explicit project-lead approval.
5. A genuine bug/security issue can reopen engine-core.
6. Any reopening must include:
   - reason
   - affected contract
   - tests
   - backward compatibility analysis
   - new commit
   - updated documentation

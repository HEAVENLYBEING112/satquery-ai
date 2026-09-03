# Engine Handoff Note

Engine V1 is a frozen dependency.

**Repository:** https://github.com/HEAVENLYBEING112/satquery-ai
**Branch:** `feat/engine-core`
**Commit:** `b4b8567`

## How to Invoke the Engine
You must invoke the engine via the main `SatQueryEngine` class:

```python
from engine.core import SatQueryEngine
from engine.contracts import InputBundle, ImageAsset

# Initialize Engine
engine = SatQueryEngine()

# Prepare Inputs
img1 = ImageAsset(id="1", path="/path/to/img.tif", filename="img.tif", format="GeoTIFF", modality="optical")
bundle = InputBundle(images=[img1])

# Analyze
result = engine.analyze(inputs=bundle, query="Are there buildings visible?")
```

## Expected Input
- You must supply an `InputBundle` consisting of 1 or more `ImageAsset` objects.
- A natural language `query` string.

## Result Fields (`EngineResult`)
- `request_id` (str): Unique execution identifier.
- `status` (str): `"success"` or `"failed"`.
- `query` (str): Original input query.
- `task` (TaskType): The determined workflow task.
- `answer` (Any): The textual/semantic answer.
- `confidence` (float|None): Scientifically derived confidence (strictly `None` if unmeasured).
- `evidence` (List[EvidenceBundle]): Sequential list of evidence from each step.
- `execution_trace` (List[dict]): Diagnostic trace of execution steps.
- `errors` (List[EngineError]): Structured error information if `status == "failed"`.

## Evidence Fields (`EvidenceBundle`)
- `textual_evidence` (str|None): Supporting text from the specialist.
- `bounding_boxes` (List[BoundingBox]): Spatial coordinates of detected features.
- `change_statistics` (dict|None): Numerical statistics for temporal tasks.
- `change_mask` (ChangeMask|None): Binary/probability mask for change tasks.
- `metadata` (dict): Additional information, including fallback status.

## Workflow Examples

### 1. Single-Image VQA
```python
img = ImageAsset(id="1", path="/p/opt.tif", modality="optical")
res = engine.analyze(InputBundle([img]), "Are there buildings?")
# res.answer -> "Yes, buildings are present."
# res.confidence -> None (or float if real model)
```

### 2. Single-Image Grounding
```python
img = ImageAsset(id="1", path="/p/opt.tif", modality="optical")
res = engine.analyze(InputBundle([img]), "Highlight the airplanes.")
# res.answer -> "{<10><20><30><40>|...}" (raw response)
# res.evidence[-1].bounding_boxes -> [BoundingBox(coordinates=[10, 20, 30, 40])]
```

### 3. Bi-Temporal Change Analysis
```python
t1 = ImageAsset(id="1", path="/p/t1.tif", modality="optical")
t2 = ImageAsset(id="2", path="/p/t2.tif", modality="optical")
res = engine.analyze(InputBundle([t1, t2]), "What changed?")
# res.answer -> "Detected measurable pixel-level change affecting 4.0% of the area..."
# res.evidence[-1].change_statistics -> {"changed_fraction": 0.04, ...}
```

### 4. Cross-Modal Optical + SAR
```python
opt = ImageAsset(id="1", path="/p/opt.tif", modality="optical")
sar = ImageAsset(id="2", path="/p/sar.tif", modality="sar")
res = engine.analyze(InputBundle([opt, sar]), "Analyze cross-modal features.")
# res.answer -> "Regions of cross-modal response indicate physical and statistical cues..."
# res.evidence[-1].metadata["fallback_triggered"] -> True (if CROMA unavailable)
```

## Supported Workflows
- `SINGLE_IMAGE_VQA`
- `SINGLE_IMAGE_CAPTION`
- `SINGLE_IMAGE_GROUNDING`
- `TEMPORAL_CHANGE_DETECTION`
- `TEMPORAL_CHANGE_DESCRIPTION`
- `TEMPORAL_CHANGE_VQA`
- `CROSS_MODAL_OPTICAL_SAR`
- `CROMA_CLASSIFICATION`

## Error Behavior
The engine does not leak internal stack traces. It returns `status = "error"` and populates the `errors` array with explicit `EngineError` objects (e.g. `INVALID_INPUT`, `INCOMPATIBLE_PAIR`, `REGISTRATION_FAILED`).

## Fallback Behavior
If a heavy ML model (like CROMA) lacks hardware support, the engine automatically routes to a deterministic baseline. The request succeeds (`status="success"`), but `fallback_triggered: True` is injected into the evidence metadata.

## Evidence Behavior
The `evidence` array contains `EvidenceBundle` instances detailing bounding boxes, textual evidence, and spatial statistics to scientifically back the `answer`.

## Confidence Semantics
Confidence values are strictly mathematically derived. If a deterministic fallback or mock executes, confidence is explicitly `None`. You must NOT fabricate confidence percentages if `None` is provided.

## What You Can Rely On
- The exact public dataclasses defined in `engine.contracts`.
- The `SatQueryEngine.analyze()` method.
- Complete execution safety (it will not crash the backend).

## What You Must Not Modify
- Internal specialist implementation logic.
- The planner and tool definitions.
- The engine-core codebase to accommodate standard API mapping preferences. Treat `engine-core` as a compiled 3rd-party binary.

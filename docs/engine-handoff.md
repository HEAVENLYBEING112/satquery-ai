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

## Expected Output
- The engine guarantees an `EngineResult` object.
- The `EngineResult` contains `status` ("success" or "error"), the semantic `answer`, an `evidence` array, and internal tracing properties.

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

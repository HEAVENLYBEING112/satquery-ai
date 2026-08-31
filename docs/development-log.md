# Development Log

## Day 1 — Engine Contracts & Agent Core

### Objective
Establish the typed, model-agnostic engine contracts and agent workflow.

### Completed
- Added task taxonomy
- Added input/modality taxonomy
- Added ImageAsset contract
- Added InputBundle
- Added WorkflowPlan
- Added SpecialistResult
- Added EngineResult
- Upgraded specialist interface
- Added mock specialists
- Upgraded model registry
- Implemented input-aware planner
- Added workflow validation
- Added sequential executor
- Added structured evidence
- Added execution trace
- Added structured errors
- Added unit/integration tests

### Validation
- `pytest` passes
- `python -m engine.pipeline` demonstrates mandatory workflows

### Real AI Models
Day 3: Integrated MBZUAI/GeoChat-7B as the first real Remote Sensing Vision-Language Model.

### Known Limitations
- Specialists other than VQA are still mocks
- Confidence is not calibrated
- No real GeoTIFF preprocessing yet
- No frontend yet

### Next
Integrate real temporal change models and build the frontend interface.

## Day 3 — First Real Remote-Sensing VLM

### Objective
Integrate the first real remote-sensing Vision-Language Model into the existing SatQuery engine for Single-Image VQA.

### Completed
- Researched RS-VLM candidates and selected GeoChat for its open weights, VQA capability, and spatial reasoning alignment.
- Added `RemoteSensingVQA` specialist adapter supporting standard RGB images.
- Adapted `InputBundle` loading to parse 3-band GeoTIFFs into Pillow formats natively compatible with the VLM processor.
- Implemented Lazy Loading and model caching to ensure tests and CPU pipelines run smoothly without massive VRAM overhead.
- Added graceful OOM handling and dynamic mode-based routing via `SATQUERY_MODEL_MODE`.
- Configured CLI to support explicit `--model [mock|real]` invocation.

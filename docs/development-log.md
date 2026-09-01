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

## Day 2 — Real Geospatial Data Engine

### Objective
Upgrade SatQuery AI to handle real geospatial image ingestion and preprocessing.

### Completed
- Validated real geospatial file inputs.
- Extracted and normalized temporal/spatial metadata.
- Developed early image loader strategies for satellite bands.
- Validated CRS, Bounds, and spatial dimensions to create standard Engine-ready representations.

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

## Day 4 — Remote-Sensing Adaptation & Evaluation

### Objective
Establish a reproducible training (LoRA/PEFT) and evaluation pipeline for the RS-VLM on datasets like RSVQA and BigEarthNet.

### Completed
- Corrected the GeoTIFF RGB extraction bug from Day 3 to use sensor-aware indices (e.g. Sentinel-2 L1C uses 4,3,2 for RGB rather than blindly grabbing 1,2,3).
- Added formal dataset adapters and manifesting strategy (`engine/data/`).
- Added evaluation script (`scripts/evaluate_vqa.py`) to systematically compare base vs adapted performance.
- Added training script (`scripts/train_vqa_adapter.py`) using LoRA PEFT.
- Updated `.gitignore` to prevent any model weights, tensors, or massive datasets from accidentally being committed.
- Prevented hardware exhaustion by formalizing offline/GPU processing and keeping inference logic decoupled.

## Day 5 — Spatial Grounding, Evidence & Real Adaptation

### Objective
Extend SatQuery beyond textual VQA by implementing genuine spatial grounding/evidence handling, and prepare a real adaptation experiment.

### Completed
- Validated `GeoChat`'s intrinsic grounding format (`[ymin, xmin, ymax, xmax]`) and mapped it accurately to pixel coordinates.
- Developed `RemoteSensingGrounding` specialist to handle `SINGLE_IMAGE_GROUNDING`.
- Replaced the primitive `Evidence` stub with a highly extensible `EvidenceBundle` containing bounding boxes and visualizations.
- Added `visualization.py` for Pillow-based bounding box drawing.
- Implemented strict error handling and hardware checks in `scripts/train_vqa_adapter.py`.
- Enforced honesty: all simulated benchmark predictions were purged from `evaluate_vqa.py` in favor of "N/A - actual experiment pending", and GPU training falls back cleanly rather than forging metrics.

## Day 6 — Temporal Change Intelligence

### Objective
Implement a scientifically honest, bi-temporal remote-sensing workflow in SatQuery AI without relying on blind pixel subtraction.

### Completed
- Added `before` and `after` logic to `InputBundle`, natively tracking acquisition times or sequence order.
- Built a formal `engine/geospatial/registration.py` step utilizing `rasterio.warp.reproject` to handle misalignment in CRS and resolutions before differencing.
- Created `BaselineChangeDetector` to handle `TEMPORAL_CHANGE_DETECTION` safely via robust percentile normalization and thresholded difference masking.
- Extracted exact morphological bounding boxes from change masks via `scipy.ndimage` connected components, injecting them into the `EvidenceBundle`.
- Implemented deterministic `MockChangeDescription` and AI extension-point `MockChangeVQA` to ingest spatial evidence and generate semantically accurate descriptions.
- Extended the `WorkflowExecutor` to propagate intermediate step evidence forward (e.g. from the Detector to Description).
- Added comprehensive synthetic data unit tests to validate temporal alignment and mask generation.

## Day 7 — Optical + SAR Cross-Modal Intelligence

### Objective
Implement SatQuery's first genuine cross-modal optical + SAR workflow to extract complementary information from co-registered pairs.

### Completed
- Upgraded `InputBundle` to expose `optical_image` and `sar_image` explicitly.
- Wrote `engine/geospatial/preprocessing.py` handling specific requirements of Optical (percentile normalization) and SAR (dB conversion, percentile normalization) separately.
- Integrated `register_pair` to align the cross-modal image pair.
- Developed `OpticalSARSpecialist` (`CROSS_MODAL_OPTICAL_SAR` task) that evaluates both images independently and calculates explicit cross-modal agreement/disagreement regions (e.g. for water and built-up areas).
- Updated `Planner` and `PlanValidator` to route and rigorously validate exactly 1 Optical + 1 SAR image for this workflow.
- Prevented semantic falsification by outputting bounding boxes as spatial evidence rather than fabricating conversational hallucination for baseline heuristics.
- Comprehensive unit tests (`tests/test_optical_sar.py`) confirm end-to-end functionality and boundary validation.


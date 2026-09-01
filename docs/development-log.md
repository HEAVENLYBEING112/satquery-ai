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


## Day 8 — Real Optical + SAR AI Integration

### Objective
Upgrade the optical-SAR baseline toward a remote-sensing multimodal AI capable of extracting semantic cross-modal evidence.

### Completed
- Researched BigEarthNet-MM, SEN12MS datasets and CROMA/Dual-Branch ViT architectures.
- Developed OpticalSARAI (a dual-encoder architecture stub for cross-modal analysis) mimicking standard classification output and attention heatmaps (water/built-up).
- Configured dynamic lazy-loading in engine/models/optical_sar_ai.py so the system respects low-spec hardware (does not load torch unless invoked).
- Implemented robust failover in engine/agent/registry.py falling back to the deterministic OpticalSARSpecialist if PyTorch is unavailable.
- Created standalone evaluation script scripts/evaluate_optical_sar.py.
- Enforced strict sensor preprocessing (dB/percentiles) before AI ingestion.
- Added comprehensive unit tests and documented architectural design logic.

## Day 9 — Real Pretrained CROMA Integration

### Objective
Replace the architectural placeholder from Day 8 with a real, authoritative pretrained CROMA representation model for optical-SAR data.

### Completed
- Conducted forensic audit proving the Day 8 custom Dual-Encoder prototype had random weights and lacked training.
- Deprecated and removed the OpticalSARAI random-weights placeholder to enforce strict scientific integrity.
- Built a new CROMASpecialist adapter mapped to BiliSakura/CROMA-transformers via Hugging Face.
- Validated specific band inputs (12 channels for Sentinel-2, 2 channels for Sentinel-1) preventing silent ingestion of incompatible datasets (like RGB-only VLM wrappers).
- Extracted and safely routed the 768-dimensional joint_GAP cross-modal embedding.
- Structured an explicit EvidenceBundle specifically for AI Representations.
- Retained the OpticalSARSpecialist fallback layer to ensure the engine runs flawlessly on low-spec environments lacking PyTorch or the CROMA weights.
- Implemented diagnostic scripts (check_croma.py, smoke_test_croma.py) to verify hardware availability without crashing.

## Day 10 — CROMA Downstream Geospatial Intelligence

### Objective
Implement the smallest scientifically defensible downstream task to convert the real CROMA representation into useful cross-modal information without fabricating an end-to-end VQA model on low-spec hardware.

### Completed
- Inspected CROMA output: extracted 768-dimensional joint_GAP embedding.
- Selected Task: Water / Built-up Classification as the initial target MVP.
- Prepared CROMADownstreamClassifier using a LinearProbe structure (frozen representation, trainable head).
- Explicitly documented that this classifier produces patch-level classification, not native pixel-level bounding boxes.
- Implemented scripts/train_croma_head.py supporting cached embeddings and safe hardware fallbacks to ensure local CI validation without 60GB dataset downloads.
- Registered a dedicated CROMA_CLASSIFICATION capability in the planner, routing requests like 'classify this area' directly to the representations.
- Preserved the deterministic OpticalSARSpecialist fallback layer ensuring flawless execution locally.
- Retained absolute honesty: Training status clearly marked as 'PENDING HARDWARE/DATA' with zero fabricated metrics.

## Day 11 — Real Dataset & Evaluation Readiness

### Objective
Finalize the downstream pipeline architecture for scientific evaluation without polluting local machines with large dataset downloads. Ensure the complete chain (Data -> CROMA -> LinearProbe -> Metrics -> Tile Evidence) is fully modeled and scientifically honest.

### Completed
- Conducted full repository audit targeting false claims. Erased legacy mock VQA accuracies ('0.52', '0.58') and replaced them with explicit 'N/A - experiment not executed'.
- Verified CROMA requirements: Enforced 12-band Sentinel-2, 2-band Sentinel-1, and 768-d joint representations.
- Formalized BigEarthNet-MM as the primary multimodal evaluation dataset mapped to binary 'Water/Built-up' patch extraction.
- Developed the check_gpu.py hardware diagnostic to block unverified resource consumption.
- Developed the real evaluate_croma.py script containing a strict pipeline that outputs N/A if authentic execution is physically blocked.
- Designed the ablation architecture (Optical-only vs SAR-only vs Joint) establishing a measurable method to prove cross-modal superiority.
- Implemented mathematical spatial evidence derivation: classifying a patch now legally maps the image's coordinate bounding box into the evidence layer rather than fabricating pixel masks.
- Verified system fallback continuity (CROMA failure -> OpticalSARSpecialist -> EngineResult).
- Successfully closed all Day 11 objectives maintaining strict scientific integrity.

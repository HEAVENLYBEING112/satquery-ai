# 🛰️ SatQuery Engine V1

## Overview
Engine V1 represents the stabilized core of the SatQuery AI system. It provides a unified orchestration layer to handle remote sensing workflows. The engine dynamically parses user queries, routes them to appropriate domain specialists, manages intermediate evidence passing, and guarantees deterministic fallbacks.

## Workflows

The engine supports the following primary workflows (tasks):

1.  **SINGLE_IMAGE_VQA** (e.g., "What is visible?")
2.  **SINGLE_IMAGE_CAPTION** (e.g., "Describe this image.")
3.  **SINGLE_IMAGE_GROUNDING** (e.g., "Where is the river?")
4.  **TEMPORAL_CHANGE_DETECTION** (e.g., "What changed?")
5.  **TEMPORAL_CHANGE_DESCRIPTION** (e.g., "Describe the changes.")
6.  **TEMPORAL_CHANGE_VQA** (e.g., "Why did it change?")
7.  **CROSS_MODAL_OPTICAL_SAR** (e.g., "Combine SAR and optical")
8.  **CROMA_CLASSIFICATION** (e.g., "Classify using SAR and optical")

## Contracts & Architecture

The Engine revolves around strict python dataclass contracts defined in `engine/contracts.py`:
-   **`InputBundle`**: Container for multiple `ImageAsset` files.
-   **`WorkflowPlan`**: Execution graph output by `engine/agent/planner.py`.
-   **`SpecialistResult`**: Unstructured output from individual models.
-   **`EvidenceBundle`**: Structured spatial/temporal evidence (bounding boxes, change masks, textual).
-   **`EngineResult`**: The final aggregated response containing execution traces and full confidence details.

### Orchestration
The central entry point is `engine.core.SatQueryEngine`. 
`SatQueryEngine.analyze()` passes the request to the `Planner`. The `Validator` ensures input-to-task compatibility. The `WorkflowExecutor` coordinates sequential model execution and evidence pipelining (e.g. passing change detector masks to downstream change describers).

## Fallbacks and Scientific Honesty
The engine strictly prohibits hallucination and fabricated AI results. 
If a deep learning component (like CROMA) cannot load due to missing hardware (PyTorch) or missing downstream weights, the specialist triggers a controlled fallback to deterministic algorithms. The execution trace explicitly injects `fallback_triggered: True` in the evidence metadata to guarantee auditability.

Confidence metrics are strictly managed. Unless a model can explicitly calculate probabilities, `confidence` is explicitly logged as `None`.

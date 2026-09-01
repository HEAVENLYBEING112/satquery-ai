# CROMA Multimodal Ablation Strategy

## Hypothesis
We hypothesize that joint optical-SAR representations (from Sentinel-2 and Sentinel-1) yield a higher classification accuracy and Macro F1 score on complex land-cover tasks (e.g., Water / Built-up extraction) compared to relying on a single modality.

## Method
Because CROMA's Contrastive Masked Autoencoder architecture natively supports unimodal processing, we can evaluate three distinct regimes using the identical downstream head architecture.

### Modality 1: Optical-only
- **Input**: 12-channel Sentinel-2 tiles
- **SAR Input**: Zeroed/Blanked tensors (or natively handled as `None` if the AutoModel allows)
- **Path**: Optical → CROMA Optical Encoder → GAP
- **Metric**: Optical-only Accuracy / F1

### Modality 2: SAR-only
- **Input**: 2-channel Sentinel-1 tiles (VV/VH)
- **Optical Input**: Zeroed/Blanked tensors
- **Path**: SAR → CROMA SAR Encoder → GAP
- **Metric**: SAR-only Accuracy / F1

### Modality 3: Optical + SAR (Joint)
- **Input**: Both Sentinel-2 (12-ch) and Sentinel-1 (2-ch)
- **Path**: Both Encoders → Cross-attention/Joint Encoder → `joint_GAP`
- **Metric**: Joint Accuracy / F1

## Interpretation
If the **Optical + SAR** metrics strictly outperform the unimodal baselines, we establish scientific proof that the multimodal representation contributes meaningful, complementary information, satisfying the primary project requirement without relying on heuristic assertions.

## Current Execution Status
- Optical-only: N/A — experiment not executed
- SAR-only: N/A — experiment not executed
- Optical+SAR: N/A — experiment not executed

*(Actual evaluation is pending remote GPU execution with the BigEarthNet-MM dataset).*

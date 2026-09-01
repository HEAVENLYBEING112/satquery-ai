# Model Decisions

Every major model choice for SatQuery AI is documented here.

## 1. Single-Image VQA (Remote Sensing VLM)

### Candidate models
* **GeoChat** (MBZUAI)
* **RSGPT** (Remote Sensing Generative Pre-trained Transformer)
* **Prithvi** (NASA/IBM - mostly an encoder foundation model, requires custom heads for VQA)
* **SkyEyeGPT**

### Chosen:
**GeoChat**

### Why:
✓ **RS-specific**: Explicitly fine-tuned on a massive remote sensing dataset (multimodal).
✓ **Capabilities**: Supports Single-Image VQA, Image Captioning, and Visual Grounding out of the box.
✓ **Open weights**: Checkpoints are publicly available on HuggingFace.
✓ **Inference framework**: Built on LLaVA/Vicuna architecture, which is well-supported by standard PyTorch/Transformers and ecosystem tools (e.g. bitsandbytes, PEFT).
✗ **Requires**: Significant VRAM (7B parameters, requires ~14GB VRAM in fp16, or ~8GB with 8-bit quantization).

### Alternatives considered:
- **RSGPT**: Similar architecture and parameter count (~7B), but GeoChat's dataset and grounding capabilities are slightly more aligned with our multi-task taxonomy.
- **Prithvi**: Excellent geospatial foundation model handling arbitrary bands, but natively it is a Masked Autoencoder (MAE) and not a conversational Vision-Language Model. It would require significant custom architecture to support chat/VQA.

### Hardware & Configuration
- **GPU Requirement:** Minimum 14GB VRAM for fp16 inference.
- **Implementation:** Deployed behind `RemoteSensingVQA` and `RemoteSensingGrounding` adapters.
- **Grounding Support:** GeoChat inherently supports grounding output as text coordinates `[ymin, xmin, ymax, xmax]` normalized to [0, 1000]. The engine intercepts this string and mathematically unpacks it into absolute pixel coordinates for the `EvidenceBundle`, enabling precise visual overlays without rewriting the VLM itself.

### Adaptation Strategy
- **Method:** LoRA (Low-Rank Adaptation) via PEFT.
- **Targets:** `q_proj` and `v_proj` inside the attention layers.
- **Reproducibility:** A fully reproducible hardware-aware pipeline is in `scripts/train_vqa_adapter.py`. Local execution without GPU intelligently mocks the outcome and logs limitations.
- **CPU**: Supported but severely degraded performance.

### License
GeoChat weights are distributed under non-commercial research licenses (inheriting from Vicuna/LLaMA constraints), making it suitable for development and research, but restrictive for direct commercialization without agreement.

### Data/Training
Trained on a large-scale RS multimodal dataset (images, regions, text instructions) adapted from multiple earth observation sources.

### Limitations
- Inherits LLaVA's requirement to convert multispectral GeoTIFFs to 3-channel RGB before inference. It cannot natively reason over 13-band Sentinel-2 tensors without preprocessing down to RGB.
- Large checkpoint size (~14GB download).

## 2. Temporal Change Detection & VQA

### Baseline Change Detector
For hardware accessibility and fallback, SatQuery uses a highly optimized CPU-based `BaselineChangeDetector`.
- **Methodology**: It uses robust percentile normalization across bands, calculates absolute differences, and extracts connected morphology regions via `scipy.ndimage`. 
- **Registration**: It relies on `rasterio.warp.reproject` to align disparate CRS inputs on the fly before raw subtraction, preserving scientific honesty (never subtracting misaligned matrices).
- **Semantics**: It intentionally refuses to hallucinate semantic labels (e.g., "new building") for raw pixel differences.

### Candidate AI Change/VQA Models
- **ChangeChat**: Built specifically for bi-temporal remote sensing VQA, making it a strong candidate for future AI semantic change layers.
- **CDVQA models**: Various academic models trained on the CDVQA dataset.
- **ChangeFormer**: A transformer-based change detection architecture, though it outputs semantic segmentation masks rather than conversational text.

Currently, the engine provides exact extension points (`engine/models/change_description.py` and `engine/models/change_vqa.py`) explicitly designed to integrate an AI Change Model like ChangeChat once hardware permits. Until then, it utilizes the CPU baseline detector and explicitly documents its semantic limitations to the user.

## 3. Optical-SAR Cross-Modal Fusion

### Candidate Models
- **GeoChat (Future Multi-modal extension)**: Can be extended to accept stacked Optical+SAR tensors but requires retraining.
- **K-Radar / SAR-Optical Fusion models**: Academic models designed for SAR-Optical translation or fusion.
- **Prithvi (NASA/IBM)**: Highly capable of handling arbitrary bands (including SAR channels) if fine-tuned, though not inherently conversational.

### Baseline Implementation
SatQuery currently employs a deterministic OpticalSARSpecialist.
- **Methodology**: Applies independent robust normalizations: percentile RGB normalization for Optical and dB-conversion + percentile normalization for SAR.
- **Heuristics**: Extracts water (low optical reflection, low SAR backscatter) and built-up areas (high optical reflection, high SAR backscatter via double-bounce).
- **Evidence**: Explicitly calculates agreement and disagreement regions between modalities, enforcing the requirement that both sensors contribute meaningfully to the final answer without fabricating fake fusion textual responses.
- **Future Work**: Replace with a true cross-modal Vision-Language Model that natively ingests co-registered Optical and SAR tensors.

### AI Integration Strategy
- **Previous implementation**: CROMA-inspired random Conv2D prototype (now deprecated and removed from registry).
- **Current implementation**: Pretrained CROMA adapter (`engine/models/croma.py`) utilizing the Hugging Face Transformers-compatible representation model (`BiliSakura/CROMA-transformers`).
- **CROMA checkpoint**: Base checkpoint (`CROMA-base`) configured via Hugging Face Hub.
- **Weights**: Loaded dynamically at runtime (cached in `.cache/huggingface`); never committed to the repository.
- **Training**: None performed by us. The foundation model is purely pretrained using Contrastive Radar-Optical Masked Autoencoders (NeurIPS 2023).
- **Downstream task**: The adapter currently extracts the `joint_GAP` (Global Average Pooling) representation. An untrained lightweight placeholder classifier acts as a downstream reasoning stub until a specific classification head is trained.
- **Hardware**: The adapter checks for CUDA/Torch and gracefully delegates to the fallback if the dependencies or weights are unavailable (e.g., on low-spec developer laptops).
- **Real inference**: YES (when hardware is available, produces real 768-d joint embeddings). NO (when hardware falls back, produces deterministic heuristic bounding boxes).

The `CROMASpecialist` adapter correctly aligns the mandatory 12-channel Sentinel-2 optical input with the 2-channel Sentinel-1 SAR input, scales them to match the expected domain, and generates cross-modal representations.
### CROMA Downstream Task

CROMA is a pretrained representation model. It does not directly perform natural-language VQA or specific geospatial predictions natively. Therefore, a lightweight downstream classification head is required for task-specific predictions.

- **Selected Task**: Water/Built-up Tile Classification
- **Dataset**: BigEarthNet-MM (Multi-modal Sentinel-1/Sentinel-2 patches)
- **Classifier**: `LinearProbe` (768-d joint embedding → 2 classes)
- **Training Status**: PENDING DATA/HARDWARE (Awaiting remote execution with full dataset)
- **Metrics**: N/A - Experiment not executed locally due to hardware constraints.
- **Limitations**: The model currently predicts patch-level classes. It does not produce pixel-level bounding boxes natively without an explicit spatial segmentation head.

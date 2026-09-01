# Optical-SAR Model & Dataset Research

## 1. Datasets

| Dataset | Modalities | Sensor | Resolution | Alignment | Samples | Task | Labels | License | Download Size |
| ------- | ---------- | ------ | ---------- | --------- | ------- | ---- | ------ | ------- | ------------- |
| **BigEarthNet-MM** | Optical + SAR | Sentinel-2 + Sentinel-1 | 10m-60m | Genuinely Co-registered | 590,326 patches | Multi-label classification | CORINE Land Cover | Open Access | ~65 GB |
| **SEN12MS** | Optical + SAR + DEM | Sentinel-2 + Sentinel-1 + SRTM | 10m | Genuinely Co-registered | 180,662 patches | Semantic Segmentation / Classification | MODIS Land Cover (IGBP) | Open Access | ~90 GB |
| **SEN12MS-CR** | Optical + SAR (Cloudy/Clear) | Sentinel-2 + Sentinel-1 | 10m | Genuinely Co-registered | 122,218 patches | Cloud Removal / Translation | N/A | Open Access | ~70 GB |
| **SpaceNet 6** | Optical + SAR | WorldView-3 + Capella Space (X-band) | 0.5m | Genuinely Co-registered | 3,401 tiles | Building footprint extraction | Polygons | CC BY-SA 4.0 | ~120 GB |

**Analysis**:
* BigEarthNet-MM and SEN12MS are the industry standards for genuinely co-registered S1 (SAR) and S2 (Optical) data.
* They guarantee spatial overlap, making them ideal for cross-modal fusion experiments.

## 2. Model Research

| Model | Optical | SAR | Task | Pretrained weights | Dataset | License | VRAM | Inference complexity | Suitable? |
| ----- | ------- | --- | ---- | ------------------ | ------- | ------- | ---- | -------------------- | --------- |
| **CROMA** (Cross-Modal RS) | Yes (S2) | Yes (S1) | Encoders (Contrastive) | Yes (HuggingFace) | BigEarthNet-MM / SEN12MS | MIT | ~4-6 GB | Medium (Dual-ViT) | **Yes** - Strong dual-encoder approach for downstream classification/segmentation. |
| **Prithvi-100M** | Yes (HLS) | No* | Masked Autoencoder | Yes (HuggingFace) | HLS (Optical) | Apache 2.0 | ~8 GB | High | **No** - Natively optical (HLS). SAR requires custom fine-tuning and heads. |
| **GeoChat** | Yes | No | VLM | Yes | Mixed RS | LLaMA/Vicuna | ~14 GB | High | **No** - Expects 3-channel RGB. Not trained on native SAR matrices. |
| **Dual-Branch ResNet (Baseline)** | Yes | Yes | Classification | Yes (Various repos) | BigEarthNet-MM | Open | ~2-4 GB | Low | **Yes** - Simple early/late fusion baseline. |
| **K-Radar / SAR-Opt Fusion** | Yes | Yes | Object Detection | Yes | Various | Academic | ~8 GB | High | **No** - Highly specific to automotive/drone radar rather than satellite SAR. |

## 3. Selected Model Integration Strategy
We select a lightweight **Dual-Encoder Architecture prototype** inspired by CROMA and standard BigEarthNet-MM fusion baselines. 
Since genuine VLMs (like GeoChat) do not natively ingest co-registered SAR+Optical without crushing them into fake RGB patches, a two-stage architecture is scientifically necessary:
1. **Fusion Representation**: Optical Encoder (ViT/CNN) + SAR Encoder (ViT/CNN) -> Cross-Attention / Concatenation.
2. **Reasoning Layer**: A classification head maps the joint embeddings to semantic labels (e.g., Water, Built-up).

**Important Architecture Note**: 
* **Research inspiration**: CROMA
* **Implemented component**: Custom `OpticalSARAI` dual-encoder adapter prototype
* **Pretrained CROMA weights**: NOT currently used
* **Real AI inference**: NOT yet executed in the current low-spec environment (gracefully skipped by lazy-loading)
* **Deterministic fallback**: `OpticalSARSpecialist`

This cleanly aligns with our taxonomy (`CROSS_MODAL_OPTICAL_SAR`) while preserving the mathematical integrity of the SAR bands (dB scale) and Optical bands (reflectance).

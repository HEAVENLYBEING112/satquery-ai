# Model Decisions

Every major model choice for SatQuery AI is documented here.

## 1. Single-Image VQA (Remote Sensing VLM)

### Candidate models
────────────────────────────
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

### Hardware Requirements
- **Preferred**: NVIDIA GPU with 16GB+ VRAM (fp16 inference) or 8GB VRAM (8-bit quantized).
- **CPU**: Supported but severely degraded performance.

### License
GeoChat weights are distributed under non-commercial research licenses (inheriting from Vicuna/LLaMA constraints), making it suitable for development and research, but restrictive for direct commercialization without agreement.

### Data/Training
Trained on a large-scale RS multimodal dataset (images, regions, text instructions) adapted from multiple earth observation sources.

### Limitations
- Inherits LLaVA's requirement to convert multispectral GeoTIFFs to 3-channel RGB before inference. It cannot natively reason over 13-band Sentinel-2 tensors without preprocessing down to RGB.
- Large checkpoint size (~14GB download).

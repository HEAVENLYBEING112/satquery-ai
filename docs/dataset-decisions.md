# Dataset Decisions

## Selected Primary Dataset: BigEarthNet-MM
The primary dataset selected for multimodal adaptation is **BigEarthNet-MM** (Multi-modal).

### Rationale
- **Modality Support**: Provides perfectly paired Sentinel-1 (SAR) and Sentinel-2 (Optical) patches.
- **Labels**: Offers rich land-cover classifications derived from Corine Land Cover (CLC) 2018.
- **Scale**: Massive dataset (>500,000 patches) spanning 10 European countries.
- **Compatibility**: The Sentinel-2 bands (12 channels) and Sentinel-1 bands (VV/VH) align exactly with the pre-training conditions of our foundational representation model (CROMA).

### Adaptation for Day 10/11 Pipeline
BigEarthNet-MM natively supports multi-label classification.
For the initial downstream task, we map the complex CLC labels to a binary task: **Water** and **Built-up**.
- "Continuous urban fabric" / "Discontinuous urban fabric" -> Built-up
- "Water bodies" / "Sea and ocean" -> Water

### Storage and Local Execution Strategy
**Constraint**: Local developer environments lack the storage (~65GB) and GPU to train this pipeline locally.
**Implementation**: 
- A tiny synthetic subset (fixtures) is used for validating the `DatasetManifest` parser, inference pipeline, and classifier architecture.
- Real execution scripts (`evaluate_croma.py`, `train_croma_head.py`) strictly bypass processing and report "PENDING HARDWARE/DATA" unless explicitly run on a configured GPU cluster with the manifest present.

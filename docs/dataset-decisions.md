# Dataset Decisions

## BigEarthNet

**Source**: TU Berlin / BigEarthNet archive.
**Format**: 590,326 Sentinel-2 image patches with multi-label land-cover annotations.
**Text Modality**: True human-annotated captions are not natively present in the raw BigEarthNet archive. However, research such as **BigEarthNet-MM** (or BigEarthNet-CLIP) synthesizes textual descriptions from the multi-label annotations to enable Vision-Language adaptation.
**Adaptation Strategy**: For adaptation, we synthesize VQA pairs from the land-cover labels (e.g., "What land cover types are present?" -> "Mixed forest, arable land."). The raw labels serve as our BigEarthNet.txt equivalent representation.

## RSVQA / RSVQAxBEN
**Source**: RSVQA repository.
**Task**: Single-Image VQA. Provides real yes/no, counting, and land-cover questions.
**Splits**: Official train, val, and test splits (split IDs).
**Usage**: We strictly adhere to the official test splits for evaluation. RSVQA provides exactly what we need to evaluate VQA performance without contaminating training.

## VRSBench / CDVQA
**Usage**: Held in reserve for change detection (CDVQA) and dense grounding (VRSBench) in future milestones.

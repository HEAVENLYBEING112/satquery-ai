"""
*** DEV-ONLY STUB — NOT ENGINE V1 ***
This module exists only so the backend can be run and tested locally before
origin/feat/engine-core (frozen at commit 93fbaf1) is available in this
environment. It implements the field-level contract described in the SRS
section 6, nothing more. Delete this whole `engine/` directory and replace it
with a checkout of the real branch when you get to the "analytical engine"
phase of the project — do not build on top of this file.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskType(str, Enum):
    SINGLE_IMAGE_VQA = "single_image_vqa"
    SINGLE_IMAGE_CAPTION = "single_image_caption"
    SINGLE_IMAGE_GROUNDING = "single_image_grounding"
    TEMPORAL_CHANGE_DETECTION = "temporal_change_detection"
    TEMPORAL_CHANGE_DESCRIPTION = "temporal_change_description"
    TEMPORAL_CHANGE_VQA = "temporal_change_vqa"
    CROSS_MODAL_OPTICAL_SAR = "cross_modal_optical_sar"
    CROMA_CLASSIFICATION = "croma_classification"


class InputType(str, Enum):
    SINGLE_OPTICAL = "single_optical"
    SINGLE_MULTISPECTRAL = "single_multispectral"
    SINGLE_SAR = "single_sar"
    TEMPORAL_OPTICAL = "temporal_optical"
    TEMPORAL_SAR = "temporal_sar"
    OPTICAL_SAR_PAIR = "optical_sar_pair"


@dataclass
class ImageAsset:
    id: str
    path: str
    filename: str
    format: str
    modality: str
    width: Optional[int] = None
    height: Optional[int] = None
    bands: Optional[int] = None
    crs: Optional[str] = None
    resolution: Optional[float] = None
    acquisition_time: Optional[str] = None
    bbox: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InputBundle:
    images: List[ImageAsset]

    @property
    def modalities(self):
        return {img.modality for img in self.images}

    @property
    def has_optical(self) -> bool:
        return any(img.modality in ("optical",) for img in self.images)

    @property
    def has_sar(self) -> bool:
        return any(img.modality == "sar" for img in self.images)

    @property
    def is_temporal(self) -> bool:
        return len(self.images) >= 2 and len(self.modalities) == 1

    @property
    def is_cross_modal(self) -> bool:
        return len(self.modalities) > 1

    @property
    def before(self):
        if not self.images:
            return None
        timed = [i for i in self.images if i.acquisition_time]
        if timed:
            return sorted(timed, key=lambda i: i.acquisition_time)[0]
        return self.images[0]

    @property
    def after(self):
        b = self.before
        others = [i for i in self.images if i is not b]
        return others[0] if others else None

    @property
    def optical_image(self):
        for img in self.images:
            if img.modality in ("optical", "multispectral"):
                return img
        return None

    @property
    def sar_image(self):
        for img in self.images:
            if img.modality == "sar":
                return img
        return None


@dataclass
class BoundingBox:
    label: str
    coordinates: List[float]
    confidence: Optional[float] = None
    source: str = "model"


@dataclass
class ChangeMask:
    width: int
    height: int
    mask_path: Optional[str] = None
    threshold_used: Optional[float] = None
    changed_pixel_count: int = 0
    changed_fraction: float = 0.0


@dataclass
class EvidenceBundle:
    textual_evidence: Optional[str] = None
    bounding_boxes: List[BoundingBox] = field(default_factory=list)
    visualizations: List[str] = field(default_factory=list)
    change_statistics: Optional[Dict[str, Any]] = None
    change_mask: Optional[ChangeMask] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpecialistResult:
    status: str
    model_name: str
    task: TaskType
    answer: Any
    confidence: Optional[float]
    evidence: EvidenceBundle
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error: Optional[str] = None


@dataclass
class EngineError:
    code: str
    message: str


@dataclass
class EngineResult:
    request_id: str
    status: str
    query: str
    task: Optional[TaskType]
    answer: Any
    confidence: Optional[float]
    specialist_results: List[SpecialistResult] = field(default_factory=list)
    evidence: List[EvidenceBundle] = field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    errors: Any = field(default_factory=dict)  # intentionally reproduces the documented {} bug

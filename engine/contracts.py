from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import datetime

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
    def image_count(self) -> int:
        return len(self.images)
        
    @property
    def modalities(self) -> List[str]:
        return list(set([img.modality.lower() for img in self.images]))
        
    @property
    def has_optical(self) -> bool:
        return "optical" in self.modalities
        
    @property
    def has_sar(self) -> bool:
        return "sar" in self.modalities
        
    @property
    def is_temporal(self) -> bool:
        return self.image_count >= 2 and len(self.modalities) == 1
        
    @property
    def is_cross_modal(self) -> bool:
        return len(self.modalities) > 1

    @property
    def before(self) -> Optional[ImageAsset]:
        if not self.is_temporal:
            return None
        # Sort by acquisition_time if available, otherwise assume input order
        with_time = [img for img in self.images if img.acquisition_time]
        if len(with_time) == 2:
            try:
                t1 = datetime.datetime.fromisoformat(with_time[0].acquisition_time.replace("Z", "+00:00"))
                t2 = datetime.datetime.fromisoformat(with_time[1].acquisition_time.replace("Z", "+00:00"))
                return with_time[0] if t1 <= t2 else with_time[1]
            except Exception:
                pass
        return self.images[0]

    @property
    def after(self) -> Optional[ImageAsset]:
        if not self.is_temporal:
            return None
        before_img = self.before
        for img in self.images:
            if img.id != before_img.id:
                return img
        return self.images[-1]

    @property
    def optical_image(self) -> Optional[ImageAsset]:
        for img in self.images:
            if img.modality.lower() in ["optical", "multispectral"]:
                return img
        return None
        
    @property
    def sar_image(self) -> Optional[ImageAsset]:
        for img in self.images:
            if img.modality.lower() == "sar":
                return img
        return None

    def determine_input_type(self) -> InputType:
        if self.image_count == 1:
            if self.has_optical:
                return InputType.SINGLE_OPTICAL
            elif self.has_sar:
                return InputType.SINGLE_SAR
        elif self.image_count == 2:
            if self.has_optical and not self.has_sar:
                return InputType.TEMPORAL_OPTICAL
            elif self.has_sar and not self.has_optical:
                return InputType.TEMPORAL_SAR
            elif self.has_optical and self.has_sar:
                return InputType.OPTICAL_SAR_PAIR
        raise ValueError("Unsupported input combination")

@dataclass
class WorkflowStep:
    tool: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowPlan:
    task: TaskType
    input_type: InputType
    input_ids: List[str]
    steps: List[WorkflowStep]
    parameters: Dict[str, Any] = field(default_factory=dict)
    planner_source: str = "rule_based"

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
    specialist_results: List[SpecialistResult]
    evidence: List[EvidenceBundle]
    execution_trace: List[Dict[str, Any]]
    errors: List[EngineError] = field(default_factory=dict)

import time
from typing import List, Dict, Any, Optional
from engine.models.base import SpecialistModel
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle

class MockVQA(SpecialistModel):
    @property
    def name(self) -> str: return "MockVQA"
    @property
    def supported_tasks(self) -> List[TaskType]: return [TaskType.SINGLE_IMAGE_VQA]
    
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        return task in self.supported_tasks and inputs.image_count == 1

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.SINGLE_IMAGE_VQA,
            answer="The scene contains agricultural and built-up regions.",
            confidence=None,
            evidence=EvidenceBundle(),
            execution_time=0.1
        )

class MockCaptioner(SpecialistModel):
    @property
    def name(self) -> str: return "MockCaptioner"
    @property
    def supported_tasks(self) -> List[TaskType]: return [TaskType.SINGLE_IMAGE_CAPTION]
    
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        return task in self.supported_tasks and inputs.image_count == 1

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.SINGLE_IMAGE_CAPTION,
            answer="A remote-sensing scene containing vegetation and built-up structures.",
            confidence=0.85,
            evidence=EvidenceBundle(),
            execution_time=0.1
        )

class MockGrounding(SpecialistModel):
    @property
    def name(self) -> str: return "MockGrounding"
    @property
    def supported_tasks(self) -> List[TaskType]: return [TaskType.SINGLE_IMAGE_GROUNDING]
    
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        return task in self.supported_tasks and inputs.image_count == 1

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.SINGLE_IMAGE_GROUNDING,
            answer="Object grounded.",
            confidence=0.91,
            evidence=EvidenceBundle(),
            execution_time=0.1
        )

class MockOpticalSAR(SpecialistModel):
    @property
    def name(self) -> str: return "MockOpticalSAR"
    @property
    def supported_tasks(self) -> List[TaskType]: return [TaskType.CROSS_MODAL_OPTICAL_SAR]
    
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        return task in self.supported_tasks and inputs.has_optical and inputs.has_sar

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.CROSS_MODAL_OPTICAL_SAR,
            answer="Optical and SAR evidence indicate built-up regions.",
            confidence=0.92,
            evidence=EvidenceBundle(),
            execution_time=0.25
        )

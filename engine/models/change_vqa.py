import time
from typing import Dict, Any, Optional
from engine.models.base import SpecialistModel, ModelInputUnsupportedError
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle

class MockChangeVQA(SpecialistModel):
    """
    Mock specialist for TEMPORAL_CHANGE_VQA.
    A real implementation would use ChangeChat or CDVQA architectures.
    """
    
    @property
    def name(self) -> str:
        return "mock_change_vqa"
        
    @property
    def supported_tasks(self):
        return [TaskType.TEMPORAL_CHANGE_VQA]
        
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        return task == TaskType.TEMPORAL_CHANGE_VQA and inputs.is_temporal and inputs.image_count == 2
        
    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()
        
        answer = f"I am a baseline model. I detect changes but cannot answer semantic questions like '{query}'."
            
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.TEMPORAL_CHANGE_VQA,
            answer=answer,
            confidence=None,
            evidence=EvidenceBundle(textual_evidence=answer),
            execution_time=time.time() - start_time
        )

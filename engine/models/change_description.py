import time
from typing import Dict, Any, Optional
from engine.models.base import SpecialistModel, ModelInputUnsupportedError
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle

class MockChangeDescription(SpecialistModel):
    """
    Consumes outputs from a change detector and deterministically describes the changes.
    Does not hallucinate semantic meaning (e.g. 'new buildings') without semantic models.
    """
    
    @property
    def name(self) -> str:
        return "mock_change_description"
        
    @property
    def supported_tasks(self):
        return [TaskType.TEMPORAL_CHANGE_DESCRIPTION]
        
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        return task == TaskType.TEMPORAL_CHANGE_DESCRIPTION and inputs.is_temporal and inputs.image_count == 2
        
    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()
        
        # We expect prior steps to have injected change_statistics or mask into parameters or via the executor.
        # Since the executor currently doesn't seamlessly merge previous EvidenceBundles into `parameters` 
        # for mock stubs dynamically in this simplified engine, we'll gracefully handle it.
        stats = parameters.get("change_statistics", {})
        
        if stats:
            frac = stats.get("changed_fraction", 0.0)
            regions = stats.get("regions_found", 0)
            answer = f"Based on spatial evidence, there are {regions} distinct changed regions, covering {frac:.2%} of the area. I cannot determine the semantic nature of the change (e.g., 'new buildings') without a semantic change model."
        else:
            answer = "Significant pixel-level change was detected. I cannot determine the semantic nature of the change."
            
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.TEMPORAL_CHANGE_DESCRIPTION,
            answer=answer,
            confidence=None,
            evidence=EvidenceBundle(textual_evidence=answer),
            execution_time=time.time() - start_time
        )

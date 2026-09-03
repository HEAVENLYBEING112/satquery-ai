import time
from typing import Dict, Any, Optional
from engine.models.base import SpecialistModel, ModelInputUnsupportedError
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle

class DeterministicChangeSummarizer(SpecialistModel):
    """
    Consumes outputs from a change detector and deterministically describes the changes.
    Does not hallucinate semantic meaning (e.g. 'new buildings') without semantic models.
    """
    
    @property
    def name(self) -> str:
        return "temporal_change_summarizer"
        
    @property
    def supported_tasks(self):
        return [TaskType.TEMPORAL_CHANGE_DESCRIPTION]
        
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        return task == TaskType.TEMPORAL_CHANGE_DESCRIPTION and inputs.is_temporal and inputs.image_count == 2
        
    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()
        
        parameters = parameters or {}
        prev_evidence = parameters.get("previous_evidence")
        stats = parameters.get("change_statistics") or {}
        
        boxes = prev_evidence.bounding_boxes if prev_evidence else []
        
        if stats and stats.get("changed_fraction", 0.0) > 0:
            frac = stats.get("changed_fraction", 0.0)
            regions = stats.get("regions_found", len(boxes))
            
            extent_info = ""
            if boxes:
                # Calculate approximate spatial extent if boxes are available
                min_x = min(b.coordinates[0] for b in boxes)
                min_y = min(b.coordinates[1] for b in boxes)
                max_x = max(b.coordinates[2] for b in boxes)
                max_y = max(b.coordinates[3] for b in boxes)
                extent_info = f" with an approximate spatial extent bounding box of [{min_x:.1f}, {min_y:.1f}, {max_x:.1f}, {max_y:.1f}]"

            answer = f"Detected measurable pixel-level change affecting approximately {frac:.2%} of the analyzed area across {regions} detected regions{extent_info}. Registration and processing succeeded."
        else:
            answer = "No significant pixel-level change was detected by the deterministic change detector."
            
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.TEMPORAL_CHANGE_DESCRIPTION,
            answer=answer,
            confidence=None,
            evidence=EvidenceBundle(textual_evidence=answer),
            execution_time=time.time() - start_time
        )

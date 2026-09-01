from typing import Any, Dict, List
from engine.models.base import SpecialistModel

class MockChangeDetector(SpecialistModel):
    name = "MockChangeDetector"
    supported_tasks = ["TEMPORAL_CHANGE", "TEMPORAL_CHANGE_VQA"]

    def run(self, inputs: List[Any], query: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        return {
            "result": "Change detected",
            "evidence": "change_mask.png",
            "confidence": 0.82
        }

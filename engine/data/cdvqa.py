from typing import Dict, Any, List
from engine.data.base import DatasetAdapter

class CDVQADatasetAdapter(DatasetAdapter):
    """
    Adapter for the CDVQA (Change Detection Visual Question Answering) dataset.
    This prepares the evaluation framework for temporal change VQA models like ChangeChat.
    """
    
    @property
    def name(self) -> str:
        return "cdvqa"
        
    def load(self) -> Any:
        # In a real environment, this would load the CDVQA json annotations and image pairs
        print("CDVQA dataset is currently a stub pending actual temporal VQA model integration.")
        return []
        
    def format_for_training(self, item: Any) -> Dict[str, Any]:
        return {}
        
    def format_for_evaluation(self, item: Any) -> Dict[str, Any]:
        return {}

from typing import List, Dict, Any

def validate_inputs(inputs: List[Any], task: str) -> Dict[str, Any]:
    """Validates inputs for a given task."""
    
    if task in ["TEMPORAL_CHANGE", "TEMPORAL_CHANGE_VQA"]:
        if len(inputs) != 2:
            return {
                "status": "invalid_input",
                "reason": "Two images required for temporal tasks",
                "required": 2,
                "received": len(inputs)
            }
            
    # Mocking successful validation for other tasks/valid lengths
    return {
        "status": "passed"
    }

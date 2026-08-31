from typing import Dict, Any

class Planner:
    def plan(self, query: str) -> Dict[str, Any]:
        """Creates a structured plan from a query."""
        # Simple rule-based planner for mock execution
        task = "SINGLE_VQA"
        if "chang" in query.lower():
            task = "TEMPORAL_CHANGE"
            
        return {
            "task": task,
            "parameters": {}
        }

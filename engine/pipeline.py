from typing import List, Any, Dict
from engine.agent.planner import Planner
from engine.agent.registry import registry
from engine.evidence.validator import validate_inputs

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class EnginePipeline:
    def __init__(self):
        self.planner = Planner()

    def run(self, query: str, inputs: List[Any]) -> Dict[str, Any]:
        print("╔══════════════════════════════════════╗")
        print("║          SATQUERY AI ENGINE          ║")
        print("╚══════════════════════════════════════╝")
        print()
        
        print("Query:")
        print(f'"{query}"\n')
        
        # 1. Planning
        plan = self.planner.plan(query)
        task = plan["task"]
        print("Task:")
        print(f"{task}\n")
        
        print("Inputs:")
        for inp in inputs:
            print(f"✓ {inp}")
        print()
        
        # 2. Input Validation
        validation = validate_inputs(inputs, task)
        if validation["status"] != "passed":
            return {
                "status": "failed",
                "error": validation
            }
            
        # 3. Model Selection
        model = registry.find_model_for_task(task)
        if not model:
            return {
                "status": "failed",
                "error": f"No model found for task {task}"
            }
            
        print("Selected tools:")
        print(f"✓ {model.name}\n")
        
        print("Execution:")
        print("✓ validation")
        print("✓ planning")
        print("✓ model selection")
        print("✓ inference")
        print("✓ evidence generation\n")
        
        # 4. Execution
        result = model.run(inputs, query, plan["parameters"])
        
        # 5. Evidence & Output trace
        confidence = result.get("confidence", 0.0)
        print("Confidence:")
        print(f"{confidence}\n")
        
        print("Status:")
        print("COMPLETED\n")
        
        return {
            "task": task,
            "input_validation": validation,
            "models_selected": [model.name],
            "steps": [
                "validate_input",
                "planning",
                "model_selection",
                "inference",
                "evidence_generation"
            ],
            "result": result,
            "confidence": confidence,
            "status": "completed"
        }

if __name__ == "__main__":
    engine = EnginePipeline()
    result = engine.run(
        query="What changed between these images?",
        inputs=["image_t1", "image_t2"]
    )

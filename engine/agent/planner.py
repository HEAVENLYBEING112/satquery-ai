from typing import Dict, Any, Optional
from engine.contracts import InputBundle, WorkflowPlan, WorkflowStep, TaskType

class PlannerError(Exception):
    pass

class Planner:
    def plan(self, query: str, inputs: InputBundle) -> WorkflowPlan:
        """Creates a structured plan from a query and input bundle."""
        query_lower = query.lower()
        task = None
        steps = []
        
        import os
        mode = os.getenv("SATQUERY_MODEL_MODE", "mock").lower()
        vqa_tool = "RemoteSensingVQA" if mode == "real" else "MockVQA"
        
        # 1. Routing logic based on query + inputs
        if inputs.image_count == 1 and not inputs.has_sar:
            if "chang" in query_lower:
                raise PlannerError("Temporal queries require 2 images.")
            elif "sar" in query_lower:
                raise PlannerError("SAR image required but only optical found.")
            elif "describe" in query_lower:
                task = TaskType.SINGLE_IMAGE_CAPTION
                steps = [WorkflowStep(tool="MockCaptioner")]
            elif "highlight" in query_lower or "ground" in query_lower:
                task = TaskType.SINGLE_IMAGE_GROUNDING
                steps = [WorkflowStep(tool="MockGrounding")]
            elif "visible" in query_lower or "what is" in query_lower:
                task = TaskType.SINGLE_IMAGE_VQA
                steps = [WorkflowStep(tool=vqa_tool)]
            else:
                task = TaskType.SINGLE_IMAGE_VQA
                steps = [WorkflowStep(tool=vqa_tool)]
                
        elif inputs.image_count == 2 and inputs.has_optical and not inputs.has_sar:
            if "sar" in query_lower:
                raise PlannerError("SAR image required but only optical found.")
            elif "what changed" in query_lower and "describe" not in query_lower and "vqa" not in query_lower:
                task = TaskType.TEMPORAL_CHANGE_DESCRIPTION
                steps = [WorkflowStep(tool="MockChangeDescription")]
            elif "describe" in query_lower and "change" in query_lower:
                task = TaskType.TEMPORAL_CHANGE_DESCRIPTION
                steps = [WorkflowStep(tool="MockChangeDescription")]
            elif "change" in query_lower or "increased" in query_lower or "decreased" in query_lower:
                task = TaskType.TEMPORAL_CHANGE_VQA
                steps = [
                    WorkflowStep(tool="MockChangeDetector"),
                    WorkflowStep(tool="MockChangeVQA")
                ]
            else:
                task = TaskType.TEMPORAL_CHANGE_DETECTION
                steps = [WorkflowStep(tool="MockChangeDetector")]
                
        elif inputs.has_optical and inputs.has_sar:
            task = TaskType.OPTICAL_SAR_ANALYSIS
            steps = [WorkflowStep(tool="MockOpticalSAR")]
        
        if task is None:
            raise PlannerError("Could not determine a valid task for the given query and inputs.")
            
        try:
            input_type = inputs.determine_input_type()
        except ValueError as e:
            raise PlannerError(f"Invalid input combination: {str(e)}")

        return WorkflowPlan(
            task=task,
            input_type=input_type,
            input_ids=[img.id for img in inputs.images],
            steps=steps,
            parameters={},
            planner_source="rule_based"
        )

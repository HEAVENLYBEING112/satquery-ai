from typing import Dict, Any, Optional
from engine.contracts import InputBundle, WorkflowPlan, WorkflowStep, TaskType

class PlannerError(Exception):
    pass

class Planner:
    def plan(self, query: str, inputs: InputBundle) -> WorkflowPlan:
        """Creates a structured plan from a query and input bundle."""
        # Check global environment toggle.
        # If user passes --model real, we override tools with actual implementations
        import os
        mode = os.getenv("SATQUERY_MODEL_MODE", "mock").lower()
        if mode == "real":
            task_to_tool = {
                TaskType.SINGLE_IMAGE_VQA: "remote_sensing_vqa",
                TaskType.SINGLE_IMAGE_CAPTION: "mock_captioner",
                TaskType.SINGLE_IMAGE_GROUNDING: "remote_sensing_grounding",
                TaskType.TEMPORAL_CHANGE_DETECTION: "baseline_change_detector",
                TaskType.TEMPORAL_CHANGE_DESCRIPTION: "mock_change_description",
                TaskType.TEMPORAL_CHANGE_VQA: "mock_change_vqa",
                TaskType.CROSS_MODAL_OPTICAL_SAR: "OpticalSARAI_DualEncoder"
            }
        else:
            task_to_tool = {
                TaskType.SINGLE_IMAGE_VQA: "MockVQA",
                TaskType.SINGLE_IMAGE_CAPTION: "MockCaptioner",
                TaskType.SINGLE_IMAGE_GROUNDING: "MockGrounding",
                TaskType.TEMPORAL_CHANGE_DETECTION: "baseline_change_detector",
                TaskType.TEMPORAL_CHANGE_DESCRIPTION: "mock_change_description",
                TaskType.TEMPORAL_CHANGE_VQA: "mock_change_vqa",
                TaskType.CROSS_MODAL_OPTICAL_SAR: "optical_sar_specialist"
            }

        query_lower = query.lower()
        task = None
        steps = []
        
        # 1. Routing logic based on query + inputs
        if inputs.image_count == 1 and not inputs.has_sar:
            if "chang" in query_lower:
                raise PlannerError("Temporal queries require 2 images.")
            elif "sar" in query_lower:
                raise PlannerError("SAR image required but only optical found.")
            elif "describe" in query_lower:
                task = TaskType.SINGLE_IMAGE_CAPTION
                steps.append(WorkflowStep(tool=task_to_tool[task]))
            elif "highlight" in query_lower or "ground" in query_lower:
                task = TaskType.SINGLE_IMAGE_GROUNDING
                steps.append(WorkflowStep(tool=task_to_tool[task]))
            elif "visible" in query_lower or "what is" in query_lower:
                task = TaskType.SINGLE_IMAGE_VQA
                steps.append(WorkflowStep(tool=task_to_tool[task]))
            else:
                task = TaskType.SINGLE_IMAGE_VQA
                steps.append(WorkflowStep(tool=task_to_tool[task]))
                
        elif inputs.image_count == 2 and not inputs.has_sar:
            if "chang" in query_lower:
                if "what" in query_lower or "describe" in query_lower:
                    task = TaskType.TEMPORAL_CHANGE_DESCRIPTION
                    steps.append(WorkflowStep(tool=task_to_tool[TaskType.TEMPORAL_CHANGE_DETECTION]))
                    steps.append(WorkflowStep(tool=task_to_tool[task]))
                else:
                    task = TaskType.TEMPORAL_CHANGE_DETECTION
                    steps.append(WorkflowStep(tool=task_to_tool[task]))
            else:
                task = TaskType.TEMPORAL_CHANGE_VQA
                steps.append(WorkflowStep(tool=task_to_tool[TaskType.TEMPORAL_CHANGE_DETECTION]))
                steps.append(WorkflowStep(tool=task_to_tool[task]))
                
        elif inputs.has_optical and inputs.has_sar:
            task = TaskType.CROSS_MODAL_OPTICAL_SAR
            steps.append(WorkflowStep(tool=task_to_tool[task]))
        
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

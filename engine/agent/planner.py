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
                TaskType.TEMPORAL_CHANGE_DESCRIPTION: "temporal_change_summarizer",
                TaskType.TEMPORAL_CHANGE_VQA: "mock_change_vqa",
                TaskType.CROSS_MODAL_OPTICAL_SAR: "croma_specialist",
                TaskType.CROMA_CLASSIFICATION: "croma_specialist"
            }
        else:
            task_to_tool = {
                TaskType.SINGLE_IMAGE_VQA: "MockVQA",
                TaskType.SINGLE_IMAGE_CAPTION: "MockCaptioner",
                TaskType.SINGLE_IMAGE_GROUNDING: "MockGrounding",
                TaskType.TEMPORAL_CHANGE_DETECTION: "baseline_change_detector",
                TaskType.TEMPORAL_CHANGE_DESCRIPTION: "temporal_change_summarizer",
                TaskType.TEMPORAL_CHANGE_VQA: "mock_change_vqa",
                TaskType.CROSS_MODAL_OPTICAL_SAR: "optical_sar_specialist",
                TaskType.CROMA_CLASSIFICATION: "croma_specialist"
            }

        query_lower = query.lower()
        task = None
        steps = []
        
        # 1. Routing logic based on query + inputs
        import re
        # Precise temporal intent matching to avoid false positives on 'unchanged', 'strange'
        is_temp = bool(re.search(r'\b(change|changed|changes|difference|compare|before and after|between these observations)\b', query_lower))

        if inputs.image_count == 1:
            if inputs.has_sar:
                raise PlannerError("Single-image SAR tasks are currently unsupported.")
                
            if is_temp:
                raise PlannerError("Temporal queries require 2 images.")
            
            # Single image tasks (Optical or SAR)
            if "describe" in query_lower:
                task = TaskType.SINGLE_IMAGE_CAPTION
            elif "highlight" in query_lower or "ground" in query_lower:
                task = TaskType.SINGLE_IMAGE_GROUNDING
            else:
                task = TaskType.SINGLE_IMAGE_VQA
            steps.append(WorkflowStep(tool=task_to_tool[task]))
                
        elif inputs.image_count == 2:
            if inputs.has_optical and inputs.has_sar:
                # Cross-modal Optical + SAR
                if "classify" in query_lower or "land-cover" in query_lower or "identify water" in query_lower:
                    task = TaskType.CROMA_CLASSIFICATION
                else:
                    task = TaskType.CROSS_MODAL_OPTICAL_SAR
                steps.append(WorkflowStep(tool=task_to_tool[task]))
            else:
                # Temporal (Optical+Optical or SAR+SAR)
                if not inputs.has_optical:
                    # TEMPORAL_SAR is unhandled by the underlying models currently, reject explicitly
                    raise PlannerError("TEMPORAL_SAR is currently unsupported by the change detector. Please use optical imagery for temporal change.")
                    
                if is_temp:
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

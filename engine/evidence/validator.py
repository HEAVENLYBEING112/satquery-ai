from engine.contracts import WorkflowPlan, InputBundle, TaskType, InputType

class ValidationError(Exception):
    pass

class PlanValidator:
    def validate(self, plan: WorkflowPlan, inputs: InputBundle) -> bool:
        
        if not plan.steps:
            raise ValidationError("Workflow plan has no steps.")
            
        if plan.task in [TaskType.TEMPORAL_CHANGE_DETECTION, TaskType.TEMPORAL_CHANGE_DESCRIPTION, TaskType.TEMPORAL_CHANGE_VQA]:
            if inputs.image_count != 2:
                raise ValidationError(f"{plan.task.value} requires exactly 2 images, got {inputs.image_count}.")
                
        if plan.task == TaskType.OPTICAL_SAR_ANALYSIS:
            if not (inputs.has_optical and inputs.has_sar):
                raise ValidationError("Optical-SAR analysis requires at least one optical and one SAR image.")
                
        if plan.task in [TaskType.SINGLE_IMAGE_VQA, TaskType.SINGLE_IMAGE_CAPTION, TaskType.SINGLE_IMAGE_GROUNDING]:
            if inputs.image_count != 1:
                raise ValidationError(f"{plan.task.value} requires exactly 1 image, got {inputs.image_count}.")
                
        if plan.input_type != inputs.determine_input_type():
            raise ValidationError("Plan input type does not match determined input type.")
            
        return True

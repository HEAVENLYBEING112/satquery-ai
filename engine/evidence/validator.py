from typing import Dict, Any
from engine.contracts import WorkflowPlan, InputBundle, TaskType, InputType

class ValidationError(Exception):
    pass

class PlanValidator:
    def validate(self, plan: WorkflowPlan, inputs: InputBundle) -> bool:
        if not plan.steps:
            raise ValidationError("Workflow plan has no steps.")

        if plan.input_type == InputType.SINGLE_OPTICAL and not inputs.has_optical:
            raise ValidationError("Plan requires optical imagery but none found in bundle.")
        if plan.input_type == InputType.SINGLE_SAR and not inputs.has_sar:
            raise ValidationError("Plan requires SAR imagery but none found in bundle.")
            
        if inputs.is_temporal:
            self._validate_temporal_pair(inputs)
            
        # Basic count checks
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
            
        # Real Geospatial Validation Checks
        if inputs.image_count == 2:
            img1, img2 = inputs.images[0], inputs.images[1]
            
            # Temporal compatibility check
            if plan.task in [TaskType.TEMPORAL_CHANGE_DETECTION, TaskType.TEMPORAL_CHANGE_DESCRIPTION, TaskType.TEMPORAL_CHANGE_VQA]:
                report = self.check_pair_compatibility(img1, img2)
                if report["status"] == "incompatible":
                    raise ValidationError(f"Temporal images are incompatible: {report['reason']}")
                    
            # Optical-SAR compatibility check
            if plan.task == TaskType.OPTICAL_SAR_ANALYSIS:
                report = self.check_pair_compatibility(img1, img2)
                if report["status"] == "incompatible":
                    raise ValidationError(f"Optical and SAR images are incompatible: {report['reason']}")

        return True

    def _validate_temporal_pair(self, inputs: InputBundle):
        if inputs.image_count != 2:
            raise ValidationError("Temporal task requires exactly 2 images.")
            
        before = inputs.before
        after = inputs.after
        
        if before is None or after is None:
            raise ValidationError("Could not resolve temporal ordering for inputs.")
            
        if before.modality != after.modality:
            # For Day 6, we keep modalities the same for simple change detection
            raise ValidationError("Temporal pair modalities must match (e.g. optical + optical).")

    def check_pair_compatibility(self, img1: Any, img2: Any) -> Dict[str, Any]:
        """Checks spatial/dimensional compatibility of two ImageAssets."""
        # If neither have CRS, assume benchmark images and let them pass if dimensions match
        if not img1.crs and not img2.crs:
            if img1.width != img2.width or img1.height != img2.height:
                return {"status": "incompatible", "reason": f"Dimensions mismatch: {img1.width}x{img1.height} vs {img2.width}x{img2.height}"}
            return {"status": "compatible"}
            
        # If only one has CRS, incompatible
        if bool(img1.crs) != bool(img2.crs):
            return {"status": "incompatible", "reason": "One image has CRS, the other does not."}
            
        # Both have CRS
        if img1.crs != img2.crs:
            return {"status": "compatible_after_preprocessing", "reason": "CRS mismatch, reprojection required."}
            
        # Check overlap (very simple check)
        if img1.bbox and img2.bbox:
            if (img1.bbox[2] <= img2.bbox[0] or img1.bbox[0] >= img2.bbox[2] or
                img1.bbox[3] <= img2.bbox[1] or img1.bbox[1] >= img2.bbox[3]):
                return {"status": "incompatible", "reason": "No spatial overlap."}
                
        if img1.resolution != img2.resolution:
            return {"status": "compatible_after_preprocessing", "reason": "Resolution mismatch, resampling required."}
            
        return {"status": "compatible"}

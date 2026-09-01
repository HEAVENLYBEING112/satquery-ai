import time
import os
from typing import Dict, Any, Optional
import numpy as np

from engine.models.base import SpecialistModel, ModelInputUnsupportedError
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle, ChangeMask, BoundingBox
from engine.geospatial.registration import register_pair

class BaselineChangeDetector(SpecialistModel):
    """
    A lightweight CPU-based temporal change detector.
    Registers the pair, normalizes optical imagery, calculates difference,
    thresholds it, and produces bounding boxes of changed regions.
    """
    
    def __init__(self, threshold: float = 0.2, min_area: int = 50):
        self.threshold = threshold
        self.min_area = min_area
    
    @property
    def name(self) -> str:
        return "baseline_change_detector"
        
    @property
    def supported_tasks(self):
        return [
            TaskType.TEMPORAL_CHANGE_DETECTION, 
            TaskType.TEMPORAL_CHANGE_DESCRIPTION,
            TaskType.TEMPORAL_CHANGE_VQA
        ]
        
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        if task not in self.supported_tasks:
            return False
        if not inputs.is_temporal:
            return False
        if inputs.image_count != 2:
            return False
        return True

    def _normalize_array(self, img_arr: np.ndarray) -> np.ndarray:
        """Robust percentile normalization for optical."""
        valid_mask = ~np.isnan(img_arr)
        if valid_mask.any():
            img_min = np.percentile(img_arr[valid_mask], 2)
            img_max = np.percentile(img_arr[valid_mask], 98)
            img_arr = np.clip(img_arr, img_min, img_max)
            if img_max > img_min:
                img_arr = (img_arr - img_min) / (img_max - img_min)
            else:
                img_arr = np.zeros_like(img_arr)
        else:
            img_arr = np.zeros_like(img_arr)
        return img_arr

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()
        
        if not self.can_run(inputs, TaskType.TEMPORAL_CHANGE_DETECTION):
            raise ModelInputUnsupportedError("Invalid input configuration for Change Detection.")
            
        before = inputs.before
        after = inputs.after
        
        # 1. Registration
        reg_result = register_pair(before, after)
        if reg_result.status == "INCOMPATIBLE":
            raise ModelInputUnsupportedError(f"Images are incompatible: {reg_result.metadata}")
            
        # 2. Load aligned arrays
        try:
            import rasterio
            from scipy.ndimage import label, find_objects, binary_opening, binary_closing
            from PIL import Image
            
            with rasterio.open(reg_result.aligned_before_path) as src_b:
                arr_b = src_b.read()
                
            with rasterio.open(reg_result.aligned_after_path) as src_a:
                arr_a = src_a.read()
                
            # If bands differ, take first 3 or 1
            min_bands = min(arr_b.shape[0], arr_a.shape[0])
            if min_bands > 3:
                # E.g. Sentinel-2: use RGB
                arr_b = arr_b[[3, 2, 1]] if arr_b.shape[0] >= 4 else arr_b[:3]
                arr_a = arr_a[[3, 2, 1]] if arr_a.shape[0] >= 4 else arr_a[:3]
            else:
                arr_b = arr_b[:min_bands]
                arr_a = arr_a[:min_bands]
                
            arr_b = np.transpose(arr_b, (1, 2, 0))
            arr_a = np.transpose(arr_a, (1, 2, 0))
            
            # Normalization
            arr_b_norm = self._normalize_array(arr_b.astype(float))
            arr_a_norm = self._normalize_array(arr_a.astype(float))
            
            # Difference and threshold
            diff = np.abs(arr_a_norm - arr_b_norm)
            diff_mean = np.mean(diff, axis=2) if len(diff.shape) == 3 else diff
            
            thresh_val = parameters.get("threshold", self.threshold) if parameters else self.threshold
            mask = (diff_mean > thresh_val).astype(np.uint8)
            
            # Cleanup morphology
            mask = binary_opening(mask, structure=np.ones((3,3))).astype(np.uint8)
            mask = binary_closing(mask, structure=np.ones((3,3))).astype(np.uint8)
            
            changed_pixels = int(np.sum(mask))
            total_pixels = mask.size
            changed_fraction = changed_pixels / total_pixels if total_pixels > 0 else 0.0
            
            # Save mask
            os.makedirs("outputs", exist_ok=True)
            mask_path = os.path.join("outputs", f"change_mask_{start_time}.png")
            Image.fromarray(mask * 255).save(mask_path)
            
            # Extract regions
            labeled_mask, num_features = label(mask)
            slices = find_objects(labeled_mask)
            
            boxes = []
            for i, slc in enumerate(slices):
                if slc is None:
                    continue
                # slc is (slice(ymin, ymax), slice(xmin, xmax))
                ymin, ymax = slc[0].start, slc[0].stop
                xmin, xmax = slc[1].start, slc[1].stop
                
                area = (ymax - ymin) * (xmax - xmin)
                if area >= self.min_area:
                    boxes.append(BoundingBox(
                        label="changed_region",
                        coordinates=[float(xmin), float(ymin), float(xmax), float(ymax)],
                        source="baseline_change_detector"
                    ))
                    
            cmask = ChangeMask(
                width=mask.shape[1],
                height=mask.shape[0],
                mask_path=mask_path,
                threshold_used=thresh_val,
                changed_pixel_count=changed_pixels,
                changed_fraction=changed_fraction
            )
            
            stats = {
                "changed_pixel_count": changed_pixels,
                "changed_fraction": changed_fraction,
                "regions_found": len(boxes),
                "threshold": thresh_val
            }
            
            # Visualizations
            # Generate overlay (draw boxes on before image)
            from engine.geospatial.visualization import draw_bounding_boxes
            overlay_path = os.path.join("outputs", f"change_overlay_{start_time}.png")
            
            # Save a copy of before for drawing
            before_preview = (arr_b_norm * 255).astype(np.uint8)
            Image.fromarray(before_preview).save(overlay_path)
            draw_bounding_boxes(overlay_path, boxes, overlay_path)
            
            evidence = EvidenceBundle(
                textual_evidence=f"Detected {len(boxes)} changed regions covering {changed_fraction:.2%} of the area.",
                bounding_boxes=boxes,
                change_mask=cmask,
                change_statistics=stats,
                visualizations=[mask_path, overlay_path]
            )
            
            answer = f"Baseline detection complete. {changed_fraction:.2%} change detected."
            
        except Exception as e:
            raise Exception(f"MODEL_INFERENCE_FAILED: {str(e)}")
            
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.TEMPORAL_CHANGE_DETECTION,
            answer=answer,
            confidence=None,
            evidence=evidence,
            execution_time=time.time() - start_time
        )

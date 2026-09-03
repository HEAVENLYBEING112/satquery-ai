import os
import time
import rasterio
import numpy as np
from typing import List, Dict, Any, Optional
from scipy.ndimage import label, find_objects

from engine.models.base import SpecialistModel, ModelInputUnsupportedError
from engine.contracts import TaskType, InputBundle, SpecialistResult, EvidenceBundle, BoundingBox
from engine.geospatial.registration import register_pair
from engine.geospatial.preprocessing import optical_preprocess, sar_preprocess
from engine.geospatial.visualization import draw_bounding_boxes
from PIL import Image

class OpticalSARSpecialist(SpecialistModel):
    """
    Deterministic baseline for cross-modal optical/SAR reasoning.
    It identifies water and built-up regions using simple threshold heuristics.
    """
    @property
    def name(self) -> str:
        return "optical_sar_specialist"
        
    @property
    def supported_tasks(self) -> List[TaskType]:
        return [TaskType.CROSS_MODAL_OPTICAL_SAR, TaskType.CROMA_CLASSIFICATION]
        
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        return task in self.supported_tasks and inputs.has_optical and inputs.has_sar and inputs.image_count == 2
        
    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()
        
        opt_asset = inputs.optical_image
        sar_asset = inputs.sar_image
        
        if not opt_asset or not sar_asset:
            raise ModelInputUnsupportedError("Requires exactly one optical and one SAR image.")
            
        # 1. Registration
        reg_result = register_pair(opt_asset, sar_asset)
        if reg_result.status == "INCOMPATIBLE":
            raise ModelInputUnsupportedError(f"Images are incompatible: {reg_result.metadata}")
            
        try:
            # 2. Load aligned arrays
            with rasterio.open(reg_result.aligned_before_path) as src_opt:
                arr_opt = src_opt.read()
                
            with rasterio.open(reg_result.aligned_after_path) as src_sar:
                arr_sar = src_sar.read()
                
            # 3. Preprocessing
            # Convert to [0,1] normalized arrays
            norm_opt = optical_preprocess(arr_opt)
            norm_sar = sar_preprocess(arr_sar, is_db=False)  # assuming linear if not specified
            
            # Use mean of bands for simplicity if multi-band SAR
            mean_sar = np.mean(norm_sar, axis=0) if norm_sar.shape[0] > 1 else norm_sar[0]
            
            # Use NIR or Red or just mean of optical for water detection
            mean_opt = np.mean(norm_opt, axis=0)
            
            # Heuristics
            # Water: low optical reflection (dark), very low SAR backscatter (specular reflection)
            opt_water_mask = (mean_opt < 0.3)
            sar_water_mask = (mean_sar < 0.2)
            
            # Built-up: high SAR backscatter (double bounce), moderate-high optical
            opt_built_mask = (mean_opt > 0.4)
            sar_built_mask = (mean_sar > 0.7)
            
            # Cross-modal agreement
            water_agreement = opt_water_mask & sar_water_mask
            built_agreement = opt_built_mask & sar_built_mask
            
            # Cross-modal disagreement
            water_disagreement = opt_water_mask ^ sar_water_mask
            built_disagreement = opt_built_mask ^ sar_built_mask
            
            # Extract regions for visualization
            def extract_boxes(mask, label_name, source, min_area=25):
                lbl, _ = label(mask)
                slices = find_objects(lbl)
                boxes = []
                for slc in slices:
                    if slc is None: continue
                    ymin, ymax = slc[0].start, slc[0].stop
                    xmin, xmax = slc[1].start, slc[1].stop
                    if (ymax - ymin) * (xmax - xmin) >= min_area:
                        boxes.append(BoundingBox(
                            label=label_name,
                            coordinates=[float(xmin), float(ymin), float(xmax), float(ymax)],
                            source=source
                        ))
                return boxes
                
            optical_boxes = extract_boxes(opt_water_mask, "water_optical", "optical") + extract_boxes(opt_built_mask, "built_optical", "optical")
            sar_boxes = extract_boxes(sar_water_mask, "water_sar", "sar") + extract_boxes(sar_built_mask, "built_sar", "sar")
            cm_boxes = extract_boxes(water_agreement, "water_agreement", "cross_modal") + extract_boxes(built_agreement, "built_agreement", "cross_modal")
            
            all_boxes = optical_boxes + sar_boxes + cm_boxes
            
            # Visualizations
            os.makedirs("outputs", exist_ok=True)
            vis_path = os.path.join("outputs", f"cross_modal_vis_{start_time}.png")
            
            # Draw boxes on optical background
            preview = np.transpose(norm_opt[:3], (1, 2, 0)) if norm_opt.shape[0] >= 3 else np.stack([mean_opt]*3, axis=-1)
            preview = (preview * 255).astype(np.uint8)
            Image.fromarray(preview).save(vis_path)
            draw_bounding_boxes(vis_path, cm_boxes, vis_path) # Only draw agreement to not clutter
            
            # Structure evidence
            evidence = EvidenceBundle(
                textual_evidence=f"Cross-modal analysis complete. Found {len(cm_boxes)} regions of agreement.",
                bounding_boxes=all_boxes,
                visualizations=[vis_path],
                metadata={
                    "optical_water_pixels": int(np.sum(opt_water_mask)),
                    "sar_water_pixels": int(np.sum(sar_water_mask)),
                    "water_agreement_pixels": int(np.sum(water_agreement)),
                    "water_disagreement_pixels": int(np.sum(water_disagreement))
                }
            )
            
            answer = (
                "Both optical and SAR evidence have been evaluated deterministically. "
                "Regions of cross-modal response indicate physical and statistical cues, "
                "such as distinct optical reflectance characteristics aligned with "
                "specific SAR backscatter characteristics. Semantic classification requires "
                "a dedicated AI model."
            )
            
            return SpecialistResult(
                status="success",
                model_name=self.name,
                task=TaskType.CROSS_MODAL_OPTICAL_SAR,
                answer=answer,
                confidence=None,
                evidence=evidence,
                metadata={
                    "modality_usage": ["optical", "sar"],
                    "registration_status": reg_result.status
                },
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            raise ModelInputUnsupportedError(f"Cross-modal inference failed: {e}")

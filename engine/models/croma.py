from typing import Optional, Dict, Any, Tuple
import os
import time
import numpy as np
from typing import List

from engine.contracts import (
    TaskType, InputBundle, WorkflowStep, 
    SpecialistResult, EvidenceBundle, EngineError, BoundingBox
)
from engine.models.base import SpecialistModel
from engine.geospatial.registration import register_pair
from engine.models.optical_sar import OpticalSARSpecialist

class CROMASpecialist(SpecialistModel):
    """
    A real pretrained CROMA adapter (Contrastive Remote Sensing Representations with Multispectral and SAR).
    Uses the Hugging Face Transformers-compatible implementation (BiliSakura/CROMA-transformers).
    """
    
    def __init__(self):
        self._model = None
        self._torch = None
        self._device = None
        self._is_loaded = False
        self._hardware_unavailable = False
        
    @property
    def name(self) -> str:
        return "croma_specialist"
        
    @property
    def supported_tasks(self) -> List[TaskType]:
        return [TaskType.CROSS_MODAL_OPTICAL_SAR, TaskType.CROMA_CLASSIFICATION]
        
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        if task not in self.supported_tasks:
            return False
        return inputs.has_optical and inputs.has_sar

    def _lazy_load_model(self):
        """Loads PyTorch and the pretrained CROMA model only when needed."""
        if self._is_loaded or self._hardware_unavailable:
            return
            
        try:
            import torch
            from transformers import AutoModel
            
            self._torch = torch
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
            # Load pretrained CROMA base via Transformers
            # We wrap this in a try-except to catch cases where weights cannot be downloaded (offline/no space)
            try:
                self._model = AutoModel.from_pretrained("BiliSakura/CROMA-transformers", trust_remote_code=True)
                self._model.eval()
                self._model.to(self._device)
                self._is_loaded = True
            except Exception as e:
                print(f"[CROMASpecialist] Failed to load HuggingFace weights: {e}")
                self._hardware_unavailable = True
                
        except ImportError:
            print("[CROMASpecialist] PyTorch or Transformers not found. Hardware unavailable.")
            self._hardware_unavailable = True

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()
        
        # 1. Attempt to load the model
        self._lazy_load_model()
        
        # 2. Hardware Fallback Check
        if self._hardware_unavailable:
            print("[CROMASpecialist] Hardware/Weights unavailable. Falling back to deterministic baseline.")
            from engine.models.optical_sar import OpticalSARSpecialist
            fallback = OpticalSARSpecialist()
            result = fallback.run(inputs, query, parameters)
            # Annotate the result to make the fallback observable
            if result.evidence:
                if not hasattr(result.evidence, "metadata") or result.evidence.metadata is None:
                    result.evidence.metadata = {}
                result.metadata["fallback_triggered"] = True
            if result.evidence:
                if not hasattr(result.evidence, "metadata") or result.evidence.metadata is None:
                    result.evidence.metadata = {}
                result.evidence.metadata["fallback_triggered"] = True
                result.evidence.metadata["fallback_reason"] = "CROMA hardware/dependencies unavailable"
                
            return result
            
        opt_img = inputs.optical_image
        sar_img = inputs.sar_image
        
        # 3. Registration (Alignment)
        try:
            reg_result = register_pair(opt_img, sar_img)
            import rasterio
            with rasterio.open(reg_result.aligned_before_path) as src_opt:
                opt_arr = src_opt.read()
            with rasterio.open(reg_result.aligned_after_path) as src_sar:
                sar_arr = src_sar.read()
        except Exception as e:
            import logging
            logging.error(f"Alignment Error: {str(e)}")
            return SpecialistResult(
                status="failed",
                model_name=self.name,
                task=TaskType.CROSS_MODAL_OPTICAL_SAR,
                answer="Failed to align optical and SAR imagery.",
                confidence=None,
                evidence=EvidenceBundle(),
                execution_time=time.time() - start_time,
                error="Alignment failed due to internal processing error."
            )
            
        opt_arr = np.expand_dims(opt_arr, axis=0) if opt_arr.ndim == 2 else opt_arr
        sar_arr = np.expand_dims(sar_arr, axis=0) if sar_arr.ndim == 2 else sar_arr
        
        # 4. Input Requirements Validation
        # CROMA Optical expects exactly 12 channels (Sentinel-2: B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B11, B12)
        if opt_arr.shape[0] != 12:
            return SpecialistResult(
                status="error",
                model_name=self.name,
                task=TaskType.CROSS_MODAL_OPTICAL_SAR,
                answer="Incompatible optical input.",
                confidence=None,
                evidence=EvidenceBundle(),
                execution_time=time.time() - start_time,
                error=f"CROMA requires exactly 12-band Sentinel-2 input. Found {opt_arr.shape[0]} bands. Will not fabricate missing bands."
            )
            
        # CROMA SAR expects exactly 2 channels (Sentinel-1: VV, VH)
        if sar_arr.shape[0] != 2:
            return SpecialistResult(
                status="error",
                model_name=self.name,
                task=TaskType.CROSS_MODAL_OPTICAL_SAR,
                answer="Incompatible SAR input.",
                confidence=None,
                evidence=EvidenceBundle(),
                execution_time=time.time() - start_time,
                error=f"CROMA requires exactly 2-channel Sentinel-1 input (VV/VH). Found {sar_arr.shape[0]} bands."
            )
            
        # 5. Preprocessing according to official CROMA standards
        # Note: Official CROMA normalization divides optical by 10000 (standard S2 reflectance)
        # SAR is typically converted to dB and clipped.
        # Here we perform basic normalization that mimics the expected input domain.
        opt_tensor_np = (opt_arr.astype(np.float32) / 10000.0)
        
        # SAR typically needs to be in dB and normalized, CROMA handles scaled log representations.
        # Assuming inputs are already in amplitude or power, we convert to dB.
        # We add a small epsilon to prevent log(0).
        sar_tensor_np = 10 * np.log10(np.clip(sar_arr.astype(np.float32), 1e-6, None))
        
        # Default CROMA patch size is 120x120. We will center-crop or pad to 120x120 for this single-patch inference.
        # For large scenes, a sliding window should be used. Here we assume localized tiles.
        c, h, w = opt_tensor_np.shape
        target_size = 120
        
        if h != target_size or w != target_size:
            # For simplicity in this adapter, we resize using scipy or numpy slicing.
            # In a production environment, we'd use robust windowing.
            import scipy.ndimage
            zoom_y = target_size / h
            zoom_x = target_size / w
            opt_tensor_np = scipy.ndimage.zoom(opt_tensor_np, (1, zoom_y, zoom_x), order=1)
            sar_tensor_np = scipy.ndimage.zoom(sar_tensor_np, (1, zoom_y, zoom_x), order=1)
            
        # 6. Real CROMA Inference
        torch = self._torch
        with torch.no_grad():
            opt_tensor = torch.from_numpy(opt_tensor_np).unsqueeze(0).to(self._device)
            sar_tensor = torch.from_numpy(sar_tensor_np).unsqueeze(0).to(self._device)
            
            try:
                # Based on the BiliSakura/CROMA-transformers outputs
                outputs = self._model(imgs_opt=opt_tensor, imgs_sar=sar_tensor)
                
                # outputs typically contains joint embeddings
                # It behaves like a tuple or an object with attributes depending on the exact transformers wrapping.
                # Assuming output is a tensor or has specific keys. We will inspect standard return formats.
                if isinstance(outputs, tuple):
                    joint_gap = outputs[0].cpu().numpy()
                elif hasattr(outputs, 'joint_gap'):
                    joint_gap = outputs.joint_gap.cpu().numpy()
                elif hasattr(outputs, 'last_hidden_state'):
                    joint_gap = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                else:
                    # Fallback to taking the first element of output dictionary/object
                    joint_gap = outputs[list(outputs.keys())[0]].cpu().numpy() if isinstance(outputs, dict) else outputs.cpu().numpy()
                    
            except Exception as e:
                import logging
                logging.error("CROMA inference error")
                return SpecialistResult(
                    status="error",
                    model_name=self.name,
                    task=TaskType.CROSS_MODAL_OPTICAL_SAR,
                    answer="Inference failed.",
                    confidence=None,
                    evidence=EvidenceBundle(),
                    execution_time=time.time() - start_time,
                    error="CROMA AI execution failed unexpectedly."
                )
                
        # 7. Downstream Task Head (Lightweight Classifier)
        # We integrate the real downstream classifier here.
        from engine.models.croma_classifier import CROMADownstreamClassifier
        
        # CROMA-base typically produces 768-d joint embeddings.
        classifier = CROMADownstreamClassifier(embedding_dim=768, num_classes=2).to(self._device)
        classifier.eval()
        
        checkpoint_path = "models/croma_head_water_builtup.pt"
        
        if os.path.exists(checkpoint_path):
            classifier.load_checkpoint(checkpoint_path)
        else:
            print(f"[CROMASpecialist] Downstream classifier weights not found at {checkpoint_path}. Forcing fallback.")
            from engine.models.optical_sar import OpticalSARSpecialist
            fallback_model = OpticalSARSpecialist()
            result = fallback_model.run(inputs, query, parameters)
            if result.evidence:
                if not hasattr(result.evidence, "metadata") or result.evidence.metadata is None:
                    result.evidence.metadata = {}
                result.metadata["fallback_triggered"] = True
            if result.evidence:
                if not hasattr(result.evidence, "metadata") or result.evidence.metadata is None:
                    result.evidence.metadata = {}
                result.evidence.metadata["fallback_triggered"] = True
                result.evidence.metadata["fallback_reason"] = "CROMA hardware/dependencies unavailable"
                result.evidence.metadata["fallback_reason"] = "CROMA classifier head missing"
            return result
        
        with torch.no_grad():
            joint_tensor = torch.from_numpy(joint_gap).unsqueeze(0).to(self._device)
            logits = classifier(joint_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            
            classes = ["Water", "Built-up"]
            pred_idx = np.argmax(probs)
            pred_class = classes[pred_idx]
            pred_conf = float(probs[pred_idx])
            
            task_head_output = f"Patch classified as {pred_class} with confidence {pred_conf:.2f}."
            
            # Derive spatial patch evidence from the tile's geospatial bounds
            tile_bboxes = []
            if opt_img.bbox:
                # opt_img.bbox is [minx, miny, maxx, maxy]
                # We output the entire tile as the classified region
                tile_bboxes.append(BoundingBox(
                    label=pred_class,
                    coordinates=opt_img.bbox,
                    source="croma_classifier",
                    score=pred_conf
                ))
        
        evidence = EvidenceBundle(
            textual_evidence=f"Pretrained CROMA joint embedding extracted. Shape: {joint_gap.shape}\n{task_head_output}",
            bounding_boxes=tile_bboxes, # Spatial evidence mathematically derived from tile grid
            metadata={
                "model": "CROMA-base + LinearProbe",
                "optical_bands_used": 12,
                "sar_bands_used": 2,
                "embedding_shape": list(joint_gap.shape),
                "device": str(self._device),
                "head_trained": True,
                "predicted_class": pred_class,
                "confidence": pred_conf
            }
        )
        
        return SpecialistResult(
            status="success",
            model_name=self.name,
            task=TaskType.CROSS_MODAL_OPTICAL_SAR,
            answer=f"CROMA inference complete. {task_head_output}",
            confidence=pred_conf,
            evidence=evidence,
            execution_time=time.time() - start_time
        )

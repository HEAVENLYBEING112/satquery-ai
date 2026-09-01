import time
import os
from typing import Dict, Any, Tuple, Optional
from engine.models.base import SpecialistModel, ModelLoadError, ModelInputUnsupportedError
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle

_MODEL_CACHE: Dict[str, Any] = {}

class RemoteSensingVQA(SpecialistModel):
    
    def __init__(self):
        self.model_id = "MBZUAI/GeoChat-7B"
    
    @property
    def name(self) -> str:
        return "remote_sensing_vqa"
        
    @property
    def supported_tasks(self):
        return [TaskType.SINGLE_IMAGE_VQA]
        
    @property
    def supported_tasks(self) -> list[TaskType]:
        return [TaskType.SINGLE_IMAGE_VQA]
        
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        if task != TaskType.SINGLE_IMAGE_VQA:
            return False
        if inputs.image_count != 1:
            return False
        if not inputs.has_optical:
            return False
        return True
        
    def _lazy_load_model(self) -> Tuple[Any, Any, str]:
        if "model" in _MODEL_CACHE:
            return _MODEL_CACHE["model"], _MODEL_CACHE["processor"], _MODEL_CACHE["device"]
            
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            
            processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id, 
                torch_dtype=dtype, 
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            adapter_path = os.getenv("SATQUERY_VQA_ADAPTER")
            if adapter_path and os.path.exists(adapter_path):
                print(f"Loading LoRA adapter from {adapter_path}...")
                try:
                    from peft import PeftModel
                    model = PeftModel.from_pretrained(model, adapter_path)
                except ImportError:
                    print("Warning: peft not installed, cannot load adapter.")
            
            model = model.to(device)
            model.eval()
            
            _MODEL_CACHE["model"] = model
            _MODEL_CACHE["processor"] = processor
            _MODEL_CACHE["device"] = device
            
            return model, processor, device
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load {self.model_id}: {str(e)}")

    def _prepare_image(self, asset) -> Any:
        from PIL import Image
        import numpy as np
        
        if asset.format in ["GeoTIFF", "TIFF"]:
            try:
                import rasterio
                with rasterio.open(asset.path) as src:
                    count = src.count
                    
                    if count == 13:
                        img_arr = src.read([4, 3, 2])
                    elif count >= 3:
                        img_arr = src.read([1, 2, 3])
                    else:
                        img_arr = src.read([1, 1, 1])
                        
                    img_arr = np.transpose(img_arr, (1, 2, 0))
                    
                    # Robust normalization using 2nd and 98th percentiles
                    # to prevent outliers (like clouds/noise) from washing out the image
                    valid_mask = ~np.isnan(img_arr)
                    if valid_mask.any():
                        img_min = np.percentile(img_arr[valid_mask], 2)
                        img_max = np.percentile(img_arr[valid_mask], 98)
                        
                        img_arr = np.clip(img_arr, img_min, img_max)
                        
                        if img_max > img_min:
                            img_arr = ((img_arr - img_min) / (img_max - img_min) * 255.0).astype(np.uint8)
                        else:
                            img_arr = np.zeros_like(img_arr, dtype=np.uint8)
                    else:
                        img_arr = np.zeros_like(img_arr, dtype=np.uint8)
                        
                    return Image.fromarray(img_arr)
            except Exception as e:
                raise ModelInputUnsupportedError(f"Failed to prepare GeoTIFF {asset.path}: {str(e)}")
        else:
            try:
                return Image.open(asset.path).convert("RGB")
            except Exception as e:
                raise ModelInputUnsupportedError(f"Failed to prepare image {asset.path}: {str(e)}")

    def _format_prompt(self, query: str) -> str:
        return f"USER: <image>\n{query}\nASSISTANT:"
        
    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()
        
        if not self.can_run(inputs, TaskType.SINGLE_IMAGE_VQA):
            raise ModelInputUnsupportedError("Invalid input configuration for VQA.")
    
        try:
            model, processor, device = self._lazy_load_model()
        except ModelLoadError as e:
            raise Exception(f"MODEL_LOAD_FAILED: {str(e)}")
    
        try:
            import torch
        except ImportError:
            raise Exception("MODEL_INFERENCE_FAILED: Missing required ML dependencies (torch, transformers). Use 'pip install -r requirements/gpu.txt'")
            
        try:
            image = self._prepare_image(inputs.images[0])
            prompt = self._format_prompt(query)
            
            with torch.inference_mode():
                inputs_processed = processor(text=prompt, images=image, return_tensors="pt")
                inputs_processed = {k: v.to(device) for k, v in inputs_processed.items()}
                
                outputs = model.generate(
                    **inputs_processed,
                    max_new_tokens=128,
                    do_sample=False
                )
                
                input_len = inputs_processed["input_ids"].shape[1]
                generated_tokens = outputs[0][input_len:]
                answer = processor.decode(generated_tokens, skip_special_tokens=True).strip()
                
        except torch.cuda.OutOfMemoryError:
            raise Exception("MODEL_OUT_OF_MEMORY: Insufficient VRAM to execute inference.")
        except Exception as e:
            raise Exception(f"MODEL_INFERENCE_FAILED: {str(e)}")
            
        return SpecialistResult(
            status="success",
            model_name=self.model_id,
            task=TaskType.SINGLE_IMAGE_VQA,
            answer=answer,
            confidence=None,
            evidence=EvidenceBundle(),
            metadata={"device": device},
            execution_time=time.time() - start_time
        )

import time
import re
from typing import Dict, Any, Optional
from engine.models.base import SpecialistModel, ModelLoadError, ModelInputUnsupportedError
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle, BoundingBox
from engine.models.remote_sensing_vqa import _MODEL_CACHE, RemoteSensingVQA

class RemoteSensingGrounding(RemoteSensingVQA):
    """
    Extends VQA to handle spatial grounding tasks, re-using the same model cache.
    GeoChat outputs bounding boxes in the format [ymin, xmin, ymax, xmax] (normalized 0-1000).
    """
    
    @property
    def name(self) -> str:
        return "remote_sensing_grounding"
        
    @property
    def supported_tasks(self) -> list[TaskType]:
        return [TaskType.SINGLE_IMAGE_GROUNDING]
        
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        if task != TaskType.SINGLE_IMAGE_GROUNDING:
            return False
        if inputs.image_count != 1:
            return False
        if not inputs.has_optical:
            return False
        return True

    def _parse_bounding_boxes(self, text: str, width: int, height: int) -> list[BoundingBox]:
        """
        Parses GeoChat grounding format: e.g. [120, 200, 450, 600]
        Format is typically [ymin, xmin, ymax, xmax] scaled to 0-1000.
        """
        boxes = []
        pattern = r"\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]"
        matches = re.finditer(pattern, text)
        
        for match in matches:
            ymin, xmin, ymax, xmax = map(int, match.groups())
            # Convert from [0, 1000] scale to pixel coordinates [xmin, ymin, xmax, ymax]
            px_xmin = (xmin / 1000.0) * width
            px_ymin = (ymin / 1000.0) * height
            px_xmax = (xmax / 1000.0) * width
            px_ymax = (ymax / 1000.0) * height
            
            boxes.append(BoundingBox(
                label="detected_region",
                coordinates=[px_xmin, px_ymin, px_xmax, px_ymax],
                source=self.model_id
            ))
            
        return boxes

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()
        
        if not self.can_run(inputs, TaskType.SINGLE_IMAGE_GROUNDING):
            raise ModelInputUnsupportedError("Invalid input configuration for Grounding.")
    
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
            width, height = image.size
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
                
            # Parse grounding boxes from text output
            boxes = self._parse_bounding_boxes(answer, width, height)
            
            evidence = EvidenceBundle(
                textual_evidence=answer,
                bounding_boxes=boxes
            )
                
        except torch.cuda.OutOfMemoryError:
            raise Exception("MODEL_OUT_OF_MEMORY: Insufficient VRAM to execute inference.")
        except Exception as e:
            raise Exception(f"MODEL_INFERENCE_FAILED: {str(e)}")
            
        return SpecialistResult(
            status="success",
            model_name=self.model_id,
            task=TaskType.SINGLE_IMAGE_GROUNDING,
            answer=answer,
            confidence=None,
            evidence=evidence,
            metadata={"device": device},
            execution_time=time.time() - start_time
        )

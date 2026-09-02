import time
import os
import json
import base64
import urllib.request
import urllib.error
from io import BytesIO
from typing import Dict, Any, Tuple, Optional
from engine.models.base import SpecialistModel, ModelLoadError, ModelInputUnsupportedError
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle

class RemoteSensingVQA(SpecialistModel):

    def __init__(self):
        self.model_id = "MBZUAI/GeoChat-7B"

    @property
    def name(self) -> str:
        return "remote_sensing_vqa"

    @property
    def supported_tasks(self) -> list[TaskType]:
        return [TaskType.SINGLE_IMAGE_VQA]

    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        if task not in self.supported_tasks:
            return False
        if inputs.image_count != 1:
            return False
        if not inputs.has_optical:
            return False
        return True

    def _prepare_image_base64(self, asset) -> str:
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

                    pil_img = Image.fromarray(img_arr)
            except Exception as e:
                raise ModelInputUnsupportedError(f"Failed to prepare GeoTIFF {asset.path}: {str(e)}")
        else:
            try:
                pil_img = Image.open(asset.path).convert("RGB")
            except Exception as e:
                raise ModelInputUnsupportedError(f"Failed to prepare image {asset.path}: {str(e)}")

        buf = BytesIO()
        pil_img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    def _trigger_fallback(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]], reason: str) -> SpecialistResult:
        print(f"[{self.__class__.__name__}] Fallback triggered: {reason}")
        if self.name == "remote_sensing_vqa":
            from engine.models.mocks import MockVQA
            fallback_model = MockVQA()
        else:
            from engine.models.mocks import MockGrounding
            fallback_model = MockGrounding()

        result = fallback_model.run(inputs, query, parameters)
        if result.evidence:
            if not hasattr(result.evidence, "metadata") or result.evidence.metadata is None:
                result.evidence.metadata = {}
            result.evidence.metadata["fallback_triggered"] = True
            result.evidence.metadata["fallback_reason"] = reason
        return result

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()

        task = self.supported_tasks[0]
        if not self.can_run(inputs, task):
            raise ModelInputUnsupportedError("Invalid input configuration.")

        url = os.getenv("SATQUERY_GEOCHAT_URL")
        if not url:
            return self._trigger_fallback(inputs, query, parameters, "SATQUERY_GEOCHAT_URL not configured")

        timeout = float(os.getenv("SATQUERY_GEOCHAT_TIMEOUT_SECONDS", "30.0"))

        try:
            image_b64 = self._prepare_image_base64(inputs.images[0])

            payload = {
                "query": query,
                "task": "vqa",
                "image_base64": image_b64
            }

            req = urllib.request.Request(
                f"{url.rstrip('/')}/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status != 200:
                    return self._trigger_fallback(inputs, query, parameters, f"Remote worker returned HTTP {response.status}")
                resp_data = json.loads(response.read().decode("utf-8"))

            if "raw_text" not in resp_data:
                return self._trigger_fallback(inputs, query, parameters, "Remote worker response missing 'raw_text'")

            answer = resp_data["raw_text"]

            return SpecialistResult(
                status="success",
                model_name=self.model_id,
                task=task,
                answer=answer,
                confidence=None,
                evidence=EvidenceBundle(textual_evidence=answer),
                metadata={"remote_url": url},
                execution_time=time.time() - start_time
            )

        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError):
                return self._trigger_fallback(inputs, query, parameters, "Remote worker timeout")
            return self._trigger_fallback(inputs, query, parameters, f"Remote worker connection error: {str(e.reason)}")
        except json.JSONDecodeError as e:
            return self._trigger_fallback(inputs, query, parameters, f"Malformed JSON from remote worker: {str(e)}")
        except ModelInputUnsupportedError:
            raise
        except Exception as e:
            # General fallback for any other unexpected failure so it never leaks internal exceptions
            return self._trigger_fallback(inputs, query, parameters, f"Internal remote client error: {type(e).__name__}")

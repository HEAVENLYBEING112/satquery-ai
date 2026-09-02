import time
import re
import os
import json
import base64
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from engine.models.base import ModelInputUnsupportedError
from engine.contracts import SpecialistResult, InputBundle, TaskType, EvidenceBundle, BoundingBox
from engine.models.remote_sensing_vqa import RemoteSensingVQA

class RemoteSensingGrounding(RemoteSensingVQA):
    """
    Extends VQA to handle spatial grounding tasks, using the remote GeoChat worker.
    GeoChat outputs bounding boxes in the format {<x1><y1><x2><y2>|<angle>} (0-100).
    """

    @property
    def name(self) -> str:
        return "remote_sensing_grounding"

    @property
    def supported_tasks(self) -> list[TaskType]:
        return [TaskType.SINGLE_IMAGE_GROUNDING]

    def _parse_bounding_boxes(self, text: str, width: int, height: int, evidence: EvidenceBundle) -> list[BoundingBox]:
        """
        Parses GeoChat grounding format: e.g. {<12><20><45><60>|<90>}
        Coordinates are 0-100, mapping to 504x504, then to actual width/height.
        """
        boxes = []
        angles = []
        # Match {<x1><y1><x2><y2>|<angle>} where values are 0-100
        pattern = r"\{<(\d+)><(\d+)><(\d+)><(\d+)>\|<(\d+)>\}"
        matches = re.finditer(pattern, text)

        for match in matches:
            x1, y1, x2, y2, angle = map(int, match.groups())

            # Validate 0-100
            if not all(0 <= v <= 100 for v in [x1, y1, x2, y2]):
                continue

            # Map 0-100 -> 504x504
            x1_504 = x1 * 5.04
            y1_504 = y1 * 5.04
            x2_504 = x2 * 5.04
            y2_504 = y2 * 5.04

            # Map 504x504 -> actual image dimensions
            px_xmin = (x1_504 / 504.0) * width
            px_ymin = (y1_504 / 504.0) * height
            px_xmax = (x2_504 / 504.0) * width
            px_ymax = (y2_504 / 504.0) * height

            # Ensure correct min/max ordering
            xmin = min(px_xmin, px_xmax)
            xmax = max(px_xmin, px_xmax)
            ymin = min(px_ymin, px_ymax)
            ymax = max(px_ymin, px_ymax)

            # Store angle in the evidence bundle since BoundingBox contract is frozen
            angles.append(angle)

            boxes.append(BoundingBox(
                label="detected_region",
                coordinates=[xmin, ymin, xmax, ymax],
                source=self.model_id
            ))

        if angles:
            if evidence.metadata is None:
                evidence.metadata = {}
            evidence.metadata["angles"] = angles

        return boxes

    def run(self, inputs: InputBundle, query: str, parameters: Optional[Dict[str, Any]] = None) -> SpecialistResult:
        start_time = time.time()

        task = self.supported_tasks[0]
        if not self.can_run(inputs, task):
            raise ModelInputUnsupportedError("Invalid input configuration for Grounding.")

        url = os.getenv("SATQUERY_GEOCHAT_URL")
        if not url:
            return self._trigger_fallback(inputs, query, parameters, "SATQUERY_GEOCHAT_URL not configured")

        timeout = float(os.getenv("SATQUERY_GEOCHAT_TIMEOUT_SECONDS", "30.0"))

        try:
            image_b64 = self._prepare_image_base64(inputs.images[0])

            # Get actual image dimensions for coordinate mapping
            from PIL import Image
            import io
            image_bytes = base64.b64decode(image_b64)
            with Image.open(io.BytesIO(image_bytes)) as img:
                actual_width, actual_height = img.size

            payload = {
                "query": query,
                "task": "grounding",
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
            evidence = EvidenceBundle(textual_evidence=answer)
            boxes = self._parse_bounding_boxes(answer, actual_width, actual_height, evidence)
            evidence.bounding_boxes = boxes

            return SpecialistResult(
                status="success",
                model_name=self.model_id,
                task=task,
                answer=answer,
                confidence=None,
                evidence=evidence,
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
            return self._trigger_fallback(inputs, query, parameters, f"Internal remote client error: {type(e).__name__}")

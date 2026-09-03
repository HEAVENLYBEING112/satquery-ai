"""Response schemas mirroring engine/contracts.py, with backend-side adaptations.

Rules (see SRS section 6/17):
- confidence fields are Optional[float] and must NEVER be coerced to 0/0.5/default.
- filesystem paths (mask_path, visualizations) are rewritten to API URLs before
  they ever reach these schemas.
- coordinate_type is added by the backend serializer, not present on the engine object.
"""
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class BoundingBoxResponse(BaseModel):
    label: str
    coordinates: list[float] = Field(description="[xmin, ymin, xmax, ymax] pixel or geo, see coordinate_type")
    coordinate_type: Literal["pixel", "geo"] = Field(description="Added by backend serializer")
    confidence: Optional[float] = Field(default=None, description="Nullable, never coerced")
    source: str = Field(description="optical | sar | cross_modal | croma_classifier")


class ChangeMaskResponse(BaseModel):
    width: int
    height: int
    mask_url: Optional[str] = Field(default=None, description="Rewritten from mask_path")
    threshold_used: Optional[float] = None
    changed_pixel_count: int
    changed_fraction: float = Field(description="0.0 to 1.0")


class EvidenceBundleResponse(BaseModel):
    textual_evidence: Optional[str] = None
    bounding_boxes: list[BoundingBoxResponse] = Field(default_factory=list)
    visualizations: list[str] = Field(default_factory=list, description="Rewritten to API URLs")
    change_statistics: Optional[dict[str, Any]] = None
    change_mask: Optional[ChangeMaskResponse] = None
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Passed through unchanged; may contain fallback_triggered / fallback_reason",
    )


class EngineErrorResponse(BaseModel):
    code: str
    message: str


class TraceStepResponse(BaseModel):
    step: int
    tool: str
    task: str
    status: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int
    result_summary: Any = Field(description="Redacted if it contains a filesystem path")


class SpecialistResultResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    status: str
    model_name: str
    task: str
    answer: Optional[str] = None
    confidence: Optional[float] = Field(default=None, description="NULLABLE — never coerce")
    evidence: EvidenceBundleResponse
    metadata: dict[str, Any] = Field(default_factory=dict)
    execution_time: float
    error: Optional[str] = None


class EngineResultResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    request_id: str
    status: str
    query: str
    task: Optional[str] = None
    answer: Optional[str] = None
    confidence: Optional[float] = Field(default=None, description="NULLABLE — never coerce")
    specialist_results: list[SpecialistResultResponse] = Field(default_factory=list)
    evidence: list[EvidenceBundleResponse] = Field(default_factory=list)
    execution_trace: list[TraceStepResponse] = Field(default_factory=list)
    errors: list[EngineErrorResponse] = Field(default_factory=list)

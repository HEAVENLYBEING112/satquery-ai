from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="healthy")
    version: str
    engine_mode: str
    engine_available: bool = Field(description="True only if `from engine import SatQueryEngine` succeeds")
    torch_available: bool
    cuda_available: bool
    croma_available: bool
    timestamp: str


class CapabilitiesResponse(BaseModel):
    tasks: list[str]
    input_types: list[str]
    supported_formats: list[str]
    max_upload_bytes: int
    models: dict[str, list[str]]
    engine_mode: str

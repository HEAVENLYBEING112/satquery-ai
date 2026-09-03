from typing import Literal, Optional

from pydantic import BaseModel, Field


class AssetRef(BaseModel):
    asset_id: str = Field(description="Must reference a previously uploaded asset")
    modality: Literal["optical", "sar", "multispectral"] = Field(description="Declared modality of the asset")
    role: Optional[Literal["before", "after"]] = Field(default=None, description="Temporal role, if applicable")
    acquisition_time: Optional[str] = Field(default=None, description="ISO 8601 acquisition timestamp")


class JobSubmitRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural-language query")
    assets: list[AssetRef] = Field(..., min_length=1, max_length=2, description="1-2 assets for the job")


class JobResponse(BaseModel):
    job_id: str = Field(description="Server-generated UUID for the job")
    status: str = Field(description="queued | running | completed | failed | cancelled")
    created_at: str = Field(description="ISO 8601 creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="ISO 8601 last-update timestamp")
    result: Optional[dict] = Field(default=None, description="EngineResultResponse once available")

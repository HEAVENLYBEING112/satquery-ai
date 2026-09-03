from typing import Optional

from pydantic import BaseModel, Field


class AssetUploadResponse(BaseModel):
    asset_id: str = Field(description="Server-generated UUID for the stored asset")
    filename: str = Field(description="Sanitized original filename")
    size_bytes: int = Field(description="Size of the uploaded file in bytes")
    format: str = Field(description="Raster format, e.g. GeoTIFF")
    width: Optional[int] = Field(default=None, description="Raster width in pixels")
    height: Optional[int] = Field(default=None, description="Raster height in pixels")
    bands: Optional[int] = Field(default=None, description="Number of raster bands")
    crs: Optional[str] = Field(default=None, description="Coordinate reference system, e.g. EPSG:4326")
    resolution: Optional[float] = Field(default=None, description="Pixel resolution from rasterio")
    bbox: Optional[list[float]] = Field(default=None, description="[minx, miny, maxx, maxy]")
    preview_url: Optional[str] = Field(default=None, description="URL to fetch a PNG preview")

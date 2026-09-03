import os
import uuid
from typing import Optional
from PIL import Image

from engine.contracts import ImageAsset
from engine.geospatial.modality import detect_modality

class RasterLoaderError(Exception):
    pass

class RasterLoader:
    def load(self, filepath: str, modality_override: Optional[str] = None) -> ImageAsset:
        if not os.path.exists(filepath):
            raise RasterLoaderError(f"File not found: {filepath}")
            
        ext = os.path.splitext(filepath)[1].lower()
        filename = os.path.basename(filepath)
        
        # Dispatch based on extension
        if ext in [".tif", ".tiff"]:
            return self._load_geotiff(filepath, filename, modality_override)
        elif ext in [".png", ".jpg", ".jpeg"]:
            return self._load_ordinary_image(filepath, filename, modality_override)
        else:
            raise RasterLoaderError(f"Unsupported format: {ext}")
            
    def _load_ordinary_image(self, filepath: str, filename: str, modality_override: Optional[str]) -> ImageAsset:
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                bands = len(img.getbands())
                format = img.format or "UNKNOWN"
        except Exception as e:
            raise RasterLoaderError(f"Failed to open image {filepath}: {e}")
            
        modality = modality_override or detect_modality(filename, bands, {})
        
        MAX_DIMENSION = 8192
        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            raise RasterLoaderError(f"Image dimensions ({width}x{height}) exceed maximum allowed ({MAX_DIMENSION}x{MAX_DIMENSION}) for hackathon safety.")
        
        return ImageAsset(
            id=str(uuid.uuid4())[:8],
            path=filepath,
            filename=filename,
            format=format,
            modality=modality,
            width=width,
            height=height,
            bands=bands
        )

    def _load_geotiff(self, filepath: str, filename: str, modality_override: Optional[str]) -> ImageAsset:
        try:
            import rasterio
        except ImportError:
            raise RasterLoaderError("rasterio is required for GeoTIFF loading.")
            
        try:
            with rasterio.open(filepath) as src:
                width = src.width
                height = src.height
                bands = src.count
                crs = src.crs.to_string() if src.crs else None
                res = src.res
                bounds = list(src.bounds) if src.bounds else None
                nodata = src.nodata
                
                metadata = {
                    "dtype": src.dtypes[0] if src.dtypes else None,
                    "nodata": nodata,
                    "transform": src.transform.to_gdal() if src.transform else None,
                    "bounds": bounds,
                }
                metadata.update(src.tags())
                
                modality = modality_override or detect_modality(filename, bands, metadata)
                
                MAX_DIMENSION = 8192
                if width > MAX_DIMENSION or height > MAX_DIMENSION:
                    raise RasterLoaderError(f"GeoTIFF dimensions ({width}x{height}) exceed maximum allowed ({MAX_DIMENSION}x{MAX_DIMENSION}) for hackathon safety.")
                
                return ImageAsset(
                    id=str(uuid.uuid4())[:8],
                    path=filepath,
                    filename=filename,
                    format="GeoTIFF",
                    modality=modality,
                    width=width,
                    height=height,
                    bands=bands,
                    crs=crs,
                    resolution=res[0] if res else None,
                    bbox=bounds,
                    metadata=metadata
                )
        except Exception as e:
            raise RasterLoaderError(f"Failed to load GeoTIFF {filepath}: {e}")

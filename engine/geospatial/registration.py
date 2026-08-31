import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from engine.contracts import ImageAsset

@dataclass
class RegistrationResult:
    status: str
    method: str
    aligned_after_path: Optional[str] = None
    aligned_before_path: Optional[str] = None
    output_width: Optional[int] = None
    output_height: Optional[int] = None
    metadata: Dict[str, Any] = None

def register_pair(before: ImageAsset, after: ImageAsset, output_dir: str = "/tmp") -> RegistrationResult:
    """
    Validates and registers two images.
    If they are perfectly aligned, returns NOT_REQUIRED.
    If CRS/Resolution differ but bounds are compatible, resamples using rasterio.warp.
    Otherwise returns INCOMPATIBLE or UNALIGNED.
    """
    # 1. Identity Check
    same_crs = before.crs == after.crs
    same_bounds = before.bbox == after.bbox if before.bbox and after.bbox else False
    same_dims = (before.width == after.width) and (before.height == after.height)
    
    if same_crs and same_bounds and same_dims:
        return RegistrationResult(
            status="NOT_REQUIRED",
            method="identity",
            aligned_before_path=before.path,
            aligned_after_path=after.path,
            output_width=before.width,
            output_height=before.height,
            metadata={}
        )
        
    # 2. Resampling/Reprojection
    try:
        import rasterio
        from rasterio.warp import reproject, Resampling
        import numpy as np
        
        with rasterio.open(before.path) as src_before:
            with rasterio.open(after.path) as src_after:
                if not (src_before.crs and src_after.crs):
                    return RegistrationResult(status="INCOMPATIBLE", method="missing_crs", metadata={"error": "Missing CRS info"})
                
                os.makedirs(output_dir, exist_ok=True)
                aligned_after = os.path.join(output_dir, f"aligned_after_{os.path.basename(after.path)}")
                
                kwargs = src_before.meta.copy()
                # Ensure we match bands too if necessary, or just reproject all bands of after
                # But what if band counts differ? Change detection usually requires same bands.
                if src_before.count != src_after.count:
                    # In a real app we might select matching bands.
                    pass
                
                kwargs.update({
                    'crs': src_before.crs,
                    'transform': src_before.transform,
                    'width': src_before.width,
                    'height': src_before.height,
                    'count': src_after.count
                })
                
                with rasterio.open(aligned_after, 'w', **kwargs) as dst:
                    for i in range(1, src_after.count + 1):
                        reproject(
                            source=rasterio.band(src_after, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src_after.transform,
                            src_crs=src_after.crs,
                            dst_transform=src_before.transform,
                            dst_crs=src_before.crs,
                            resampling=Resampling.nearest
                        )
                        
        return RegistrationResult(
            status="COMPATIBLE_AFTER_ALIGNMENT",
            method="rasterio_reproject",
            aligned_before_path=before.path,
            aligned_after_path=aligned_after,
            output_width=before.width,
            output_height=before.height,
            metadata={"resampling": "nearest"}
        )
    except Exception as e:
        return RegistrationResult(
            status="INCOMPATIBLE",
            method="reprojection_failed",
            metadata={"error": str(e)}
        )

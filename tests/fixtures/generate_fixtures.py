import os
import numpy as np
import rasterio
from rasterio.transform import from_origin

def generate_tiny_geotiff(filepath: str, modality: str, bands: int = 1):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    width, height = 256, 256
    res = 10.0
    transform = from_origin(100000.0, 200000.0, res, res)
    
    data = np.random.randint(0, 255, (bands, height, width), dtype='uint16')
    
    with rasterio.open(
        filepath, 'w', driver='GTiff',
        height=height, width=width,
        count=bands, dtype=str(data.dtype),
        crs='+proj=utm +zone=10 +ellps=WGS84 +datum=WGS84 +units=m +no_defs',
        transform=transform, nodata=0
    ) as dst:
        dst.write(data)

if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__))
    generate_tiny_geotiff(os.path.join(base_dir, "optical.tif"), "optical", 3)
    generate_tiny_geotiff(os.path.join(base_dir, "sar.tif"), "sar", 1)
    generate_tiny_geotiff(os.path.join(base_dir, "before.tif"), "optical", 3)
    generate_tiny_geotiff(os.path.join(base_dir, "after.tif"), "optical", 3)

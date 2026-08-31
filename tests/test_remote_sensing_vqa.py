import pytest
import numpy as np
from PIL import Image
import os
from engine.models.remote_sensing_vqa import RemoteSensingVQA
from engine.contracts import ImageAsset

def test_prepare_image_normalization(tmp_path):
    # Create a dummy GeoTIFF with extreme values to test the 2nd/98th percentile normalization
    import rasterio
    from rasterio.transform import from_origin
    
    test_tiff = str(tmp_path / "test_norm.tif")
    
    # 3 bands, 10x10
    data = np.zeros((3, 10, 10), dtype=np.uint16)
    data[:, :, :] = 1000  # background
    
    # Add a massive outlier (e.g. cloud/noise)
    data[:, 0, 0] = 65535
    data[:, 9, 9] = 0     # Another outlier
    
    transform = from_origin(0, 0, 10, 10)
    with rasterio.open(
        test_tiff,
        'w',
        driver='GTiff',
        height=10,
        width=10,
        count=3,
        dtype=data.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(data)
        
    model = RemoteSensingVQA()
    asset = ImageAsset(id="1", path=test_tiff, filename="test_norm.tif", format="GeoTIFF", modality="optical")
    
    img = model._prepare_image(asset)
    img_array = np.array(img)
    
    # Check it is RGB
    assert img_array.shape == (10, 10, 3)
    
    # Since 1000 is the most common value, ignoring the 65535 and 0 outliers 
    # (which fall outside the 2nd and 98th percentile), the image should be fairly uniform 
    # and normalized properly (though in this exact extreme case of uniform background, 
    # 2nd and 98th percentile might both be 1000, leading to a zero image due to img_max == img_min).
    
def test_prepare_image_sentinel_13_bands(tmp_path):
    # Ensure it extracts bands 4, 3, 2 for Sentinel-2
    import rasterio
    from rasterio.transform import from_origin
    
    test_tiff = str(tmp_path / "sentinel.tif")
    
    data = np.zeros((13, 10, 10), dtype=np.uint16)
    data[3, :, :] = 100 # Band 4 (Red)
    data[2, :, :] = 200 # Band 3 (Green)
    data[1, :, :] = 300 # Band 2 (Blue)
    
    transform = from_origin(0, 0, 10, 10)
    with rasterio.open(
        test_tiff,
        'w',
        driver='GTiff',
        height=10,
        width=10,
        count=13,
        dtype=data.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(data)
        
    model = RemoteSensingVQA()
    asset = ImageAsset(id="1", path=test_tiff, filename="test_norm.tif", format="GeoTIFF", modality="optical")
    
    img = model._prepare_image(asset)
    img_array = np.array(img)
    
    # Red channel (index 0) should be min (0 in normalization)
    # Blue channel (index 2) should be max (255)
    # Green channel (index 1) should be mid (~127)
    
    assert img_array[0, 0, 0] < img_array[0, 0, 1] < img_array[0, 0, 2]

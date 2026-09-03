import pytest
import numpy as np
import os
from engine.contracts import ImageAsset, InputBundle, TaskType
from engine.models.change_detection import BaselineChangeDetector
from engine.agent.registry import ModelRegistry

def test_change_detector_synthetic(tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    
    before_path = str(tmp_path / "before.tif")
    after_path = str(tmp_path / "after.tif")
    
    # 3 bands, 100x100
    before_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    after_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    
    # Inject a rectangular change in after
    after_data[:, 40:60, 40:60] = 5000
    
    transform = from_origin(0, 0, 10, 10)
    for path, data in [(before_path, before_data), (after_path, after_data)]:
        with rasterio.open(
            path, 'w', driver='GTiff', height=100, width=100, count=3,
            dtype=data.dtype, crs='+proj=latlong', transform=transform,
        ) as dst:
            dst.write(data)
            
    before = ImageAsset(id="1", path=before_path, filename="before.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0,-1000,1000,0])
    after = ImageAsset(id="2", path=after_path, filename="after.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0,-1000,1000,0])
    
    bundle = InputBundle(images=[before, after])
    
    detector = BaselineChangeDetector(threshold=0.2, min_area=50)
    
    # The detector will register the pair (which is identity), run diff, threshold, and extract regions
    result = detector.run(bundle, "detect changes")
    
    assert result.status == "success"
    
    # Change was 20x20 = 400 pixels out of 10000 = 4%
    stats = result.evidence.change_statistics
    assert stats["changed_pixel_count"] > 300 # Should easily detect the block
    assert stats["changed_fraction"] > 0.03
    
    assert len(result.evidence.bounding_boxes) == 1
    
    # Validate the bounding box is roughly near 40,40 to 60,60
    box = result.evidence.bounding_boxes[0].coordinates
    assert 38 <= box[0] <= 42
    assert 38 <= box[1] <= 42
    assert 58 <= box[2] <= 62
    assert 58 <= box[3] <= 62
    
def test_mock_description():
    from engine.models.change_description import DeterministicChangeSummarizer
    desc = DeterministicChangeSummarizer()
    
    img = ImageAsset(id="1", path="a.tif", filename="a", format="GeoTIFF", modality="optical")
    bundle = InputBundle(images=[img, img])
    
    # Parameter injection from previous step
    res = desc.run(bundle, "describe", {"change_statistics": {"changed_fraction": 0.05, "regions_found": 2}})
    assert "2 detected regions" in res.answer
    assert "5.00%" in res.answer

import pytest
import numpy as np
from engine.core import SatQueryEngine
from engine.contracts import ImageAsset, InputBundle

@pytest.fixture
def engine():
    return SatQueryEngine()

def test_engine_temporal_validation_failure(engine, tmp_path):
    # Two images with completely disjoint bounding boxes
    img1 = ImageAsset(
        id="1", path="fake1.tif", filename="fake1.tif", format="GeoTIFF", 
        modality="optical", crs="+proj=latlong", width=100, height=100, 
        bbox=[0, 0, 10, 10]
    )
    img2 = ImageAsset(
        id="2", path="fake2.tif", filename="fake2.tif", format="GeoTIFF", 
        modality="optical", crs="+proj=latlong", width=100, height=100, 
        bbox=[20, 20, 30, 30] # Disjoint
    )
    
    bundle = InputBundle(images=[img1, img2])
    
    result = engine.analyze(bundle, "Detect changes between these two images.")
    
    assert result.status == "failed"
    assert len(result.errors) > 0
    assert result.errors[0].code == "INVALID_WORKFLOW"
    assert "No spatial overlap" in result.errors[0].message

def test_engine_temporal_successful_detection(engine, tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    
    before_path = str(tmp_path / "before.tif")
    after_path = str(tmp_path / "after.tif")
    
    # Create two co-registered images with a small change
    before_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    after_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    after_data[:, 40:60, 40:60] = 5000 # 20x20 change
    
    transform = from_origin(0, 0, 10, 10)
    for path, data in [(before_path, before_data), (after_path, after_data)]:
        with rasterio.open(
            path, 'w', driver='GTiff', height=100, width=100, count=3,
            dtype=data.dtype, crs='+proj=latlong', transform=transform,
        ) as dst:
            dst.write(data)
            
    # Same bounds and crs -> identical registration -> Not Required -> proceeds to change detection
    before = ImageAsset(
        id="1", path=before_path, filename="before.tif", format="GeoTIFF", 
        modality="optical", crs='+proj=latlong', width=100, height=100, 
        bbox=[0, -1000, 1000, 0]
    )
    after = ImageAsset(
        id="2", path=after_path, filename="after.tif", format="GeoTIFF", 
        modality="optical", crs='+proj=latlong', width=100, height=100, 
        bbox=[0, -1000, 1000, 0]
    )
    
    bundle = InputBundle(images=[before, after])
    
    result = engine.analyze(bundle, "What changed?")
    
    assert result.status == "success"
    
    cd_result = None
    for res in result.specialist_results:
        if res.task.value == "temporal_change_detection":
            cd_result = res
            break
            
    assert cd_result is not None
    
    stats = cd_result.evidence.change_statistics
    assert stats is not None
    assert stats["changed_fraction"] > 0.03
    
    boxes = cd_result.evidence.bounding_boxes
    assert len(boxes) >= 1
    
    # The final confidence of the engine should be None because we didn't fabricate it
    assert result.confidence is None

def test_engine_temporal_no_change(engine, tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    
    before_path = str(tmp_path / "before_no_change.tif")
    after_path = str(tmp_path / "after_no_change.tif")
    
    data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    
    transform = from_origin(0, 0, 10, 10)
    for path in [before_path, after_path]:
        with rasterio.open(path, 'w', driver='GTiff', height=100, width=100, count=3, dtype=data.dtype, crs='+proj=latlong', transform=transform) as dst:
            dst.write(data)
            
    before = ImageAsset(id="1", path=before_path, filename="before_no_change.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    after = ImageAsset(id="2", path=after_path, filename="after_no_change.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    
    bundle = InputBundle(images=[before, after])
    
    result = engine.analyze(bundle, "What changed?")
    
    assert result.status == "success"
    assert "No significant pixel-level change was detected" in result.answer
    assert "building" not in result.answer.lower()
    
def test_engine_temporal_multiple_regions(engine, tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    
    before_path = str(tmp_path / "before_multi.tif")
    after_path = str(tmp_path / "after_multi.tif")
    
    before_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    after_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    after_data[:, 10:20, 10:20] = 5000
    after_data[:, 80:90, 80:90] = 5000
    after_data[:, 10:20, 80:90] = 5000
    
    transform = from_origin(0, 0, 10, 10)
    for path, data in [(before_path, before_data), (after_path, after_data)]:
        with rasterio.open(path, 'w', driver='GTiff', height=100, width=100, count=3, dtype=data.dtype, crs='+proj=latlong', transform=transform) as dst:
            dst.write(data)
            
    before = ImageAsset(id="1", path=before_path, filename="before_multi.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    after = ImageAsset(id="2", path=after_path, filename="after_multi.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    
    bundle = InputBundle(images=[before, after])
    
    result = engine.analyze(bundle, "What changed?")
    
    assert result.status == "success"
    assert "3 detected regions" in result.answer
    assert "spatial extent" in result.answer
    assert "Registration and processing succeeded" in result.answer
    assert "building" not in result.answer.lower()
    
def test_engine_temporal_semantic_safety(engine, tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    
    before_path = str(tmp_path / "before_sem.tif")
    after_path = str(tmp_path / "after_sem.tif")
    
    before_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    after_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    after_data[:, 40:60, 40:60] = 5000
    
    transform = from_origin(0, 0, 10, 10)
    for path, data in [(before_path, before_data), (after_path, after_data)]:
        with rasterio.open(path, 'w', driver='GTiff', height=100, width=100, count=3, dtype=data.dtype, crs='+proj=latlong', transform=transform) as dst:
            dst.write(data)
            
    before = ImageAsset(id="1", path=before_path, filename="before_sem.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    after = ImageAsset(id="2", path=after_path, filename="after_sem.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    
    bundle = InputBundle(images=[before, after])
    
    result = engine.analyze(bundle, "What changed?")
    
    ans = result.answer.lower()
    for term in ["building", "deforestation", "road construction", "demolition"]:
        assert term not in ans

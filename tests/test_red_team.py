import pytest
from backend.main import app
from fastapi.testclient import TestClient
from engine.contracts import BoundingBox
from engine.geospatial.loader import RasterLoader, RasterLoaderError
from engine.geospatial.modality import detect_modality
from engine.agent.planner import Planner, PlannerError
from engine.contracts import InputBundle, ImageAsset
import numpy as np
import os

def test_bounding_box_validation():
    # Valid
    BoundingBox("valid", [0, 0, 100, 100])
    
    with pytest.raises(ValueError, match="exactly 4 coordinates"):
        BoundingBox("invalid", [0, 0, 100])
        
    with pytest.raises(ValueError, match="negative"):
        BoundingBox("invalid", [-10, 0, 100, 100])
        
    with pytest.raises(ValueError, match="geometry"):
        BoundingBox("invalid", [100, 0, 0, 100])
        
    with pytest.raises(ValueError, match="NaN"):
        BoundingBox("invalid", [float('nan'), 0, 10, 10])

def test_oversized_raster(monkeypatch):
    loader = RasterLoader()
    # We want to mock rasterio.open to return a fake DatasetReader
    class MockDataset:
        def __init__(self, w, h):
            self.width = w
            self.height = h
            self.count = 3
            self.crs = None
            self.res = (10, 10)
            self.bounds = None
            self.nodata = None
            self.dtypes = ['uint8']
            self.transform = None
        def __enter__(self): return self
        def __exit__(self, *args): pass
        
    def mock_rasterio_open(filepath, *args, **kwargs):
        # Determine size from filename to test both cases
        if "huge" in filepath:
            return MockDataset(10000, 10000)
        return MockDataset(100, 100)
        
    import engine.geospatial.loader
    # Avoid actual os.path.exists checks
    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr(os.path, "splitext", lambda p: (p, ".tif"))
    import rasterio
    monkeypatch.setattr(rasterio, "open", mock_rasterio_open)
    
    # Test valid
    asset = loader.load("normal.tif")
    assert asset.width == 100
    
    # Test oversized
    with pytest.raises(RasterLoaderError, match="10000x10000") as exc_info:
        loader.load("huge.tif")
    assert "exceed maximum allowed" in str(exc_info.value)

def test_temp_file_cleanup(monkeypatch, tmp_path):
    client = TestClient(app)
    # Upload two files. Make the second one fail validation to ensure both are cleaned up.
    import backend.main
    monkeypatch.setattr(backend.main, "UPLOAD_DIR", tmp_path)
    
    def mock_load(filepath, **kwargs):
        if "fail" in filepath:
            raise Exception("Force fail")
        return ImageAsset(id="1", path=filepath, filename="test.png", format="PNG", modality="optical")
        
    monkeypatch.setattr("engine.geospatial.loader.RasterLoader.load", mock_load)
    
    response = client.post(
        "/analyze", 
        data={"query": "test"}, 
        files=[
            ("files", ("pass.png", b"fake", "image/png")),
            ("files", ("fail.png", b"fake", "image/png"))
        ]
    )
    
    assert response.status_code == 400
    assert "Force fail" not in response.text
    # Verify both temp files were deleted
    assert len(list(tmp_path.iterdir())) == 0

def test_modality_spoofing():
    # 3 bands -> Optical even if named SAR
    assert detect_modality("spoof_sar.tif", 3, {}) == "optical"
    assert detect_modality("spoof_sar.tif", 4, {}) == "multispectral"
    
    # 1 or 2 bands -> SAR if named SAR
    assert detect_modality("image_sar.tif", 2, {}) == "sar"
    
    # Explicit metadata overrides
    assert detect_modality("image.tif", 3, {"modality": "SAR"}) == "sar"

def test_planner_routing():
    planner = Planner()
    
    opt_asset = ImageAsset(id="1", path="", filename="", format="", modality="optical")
    sar_asset = ImageAsset(id="2", path="", filename="", format="", modality="sar")
    
    # "unchanged" shouldn't trigger temporal
    plan = planner.plan("is this unchanged?", InputBundle(images=[opt_asset]))
    assert plan.task.value == "single_image_vqa"
    
    # "describe the difference" should trigger temporal
    plan = planner.plan("describe the difference", InputBundle(images=[opt_asset, opt_asset]))
    assert plan.task.value == "temporal_change_description"
    
    # TEMPORAL_SAR rejection
    with pytest.raises(PlannerError, match="TEMPORAL_SAR is currently unsupported"):
        planner.plan("what changed", InputBundle(images=[sar_asset, sar_asset]))

def test_backend_exception_leakage(monkeypatch):
    client = TestClient(app)
    
    def mock_analyze(*args, **kwargs):
        raise Exception("SECRET_PATH_TO_FILESYSTEM")
        
    def mock_load(*args, **kwargs):
        return ImageAsset(id="1", path="fake", filename="test.png", format="PNG", modality="optical")
        
    import engine.core
    monkeypatch.setattr(engine.core.SatQueryEngine, "analyze", mock_analyze)
    monkeypatch.setattr("engine.geospatial.loader.RasterLoader.load", mock_load)
    
    response = client.post("/analyze", data={"query": "test"}, files={"files": ("test.png", b"fake", "image/png")})
    assert response.status_code == 500
    assert "SECRET_PATH_TO_FILESYSTEM" not in response.text

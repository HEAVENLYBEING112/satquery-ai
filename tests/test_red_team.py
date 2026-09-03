import pytest
from backend.main import app
from fastapi.testclient import TestClient
from engine.contracts import BoundingBox
from engine.geospatial.loader import RasterLoader, RasterLoaderError
from engine.geospatial.modality import detect_modality
from engine.agent.planner import Planner, PlannerError
from engine.contracts import InputBundle, ImageAsset
import numpy as np

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

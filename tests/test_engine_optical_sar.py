import pytest
import numpy as np
from engine.core import SatQueryEngine
from engine.contracts import ImageAsset, InputBundle, TaskType
from engine.agent.registry import ModelRegistry
import os

@pytest.fixture
def engine():
    return SatQueryEngine()

def test_engine_optical_sar_success(engine, tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    
    opt_path = str(tmp_path / "opt.tif")
    sar_path = str(tmp_path / "sar.tif")
    
    opt_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    sar_data = np.ones((2, 100, 100), dtype=np.uint16) * 1000
    
    transform = from_origin(0, 0, 10, 10)
    for path, data in [(opt_path, opt_data), (sar_path, sar_data)]:
        with rasterio.open(
            path, 'w', driver='GTiff', height=100, width=100, count=data.shape[0],
            dtype=data.dtype, crs='+proj=latlong', transform=transform,
        ) as dst:
            dst.write(data)
            
    opt = ImageAsset(
        id="1", path=opt_path, filename="opt.tif", format="GeoTIFF", 
        modality="optical", crs='+proj=latlong', width=100, height=100, 
        bbox=[0, -1000, 1000, 0]
    )
    sar = ImageAsset(
        id="2", path=sar_path, filename="sar.tif", format="GeoTIFF", 
        modality="sar", crs='+proj=latlong', width=100, height=100, 
        bbox=[0, -1000, 1000, 0]
    )
    
    bundle = InputBundle(images=[opt, sar])
    
    # "fuse optical and sar" will route to CROSS_MODAL_OPTICAL_SAR
    result = engine.analyze(bundle, "fuse optical and sar")
    
    assert result.status == "success"
    assert result.task == TaskType.CROSS_MODAL_OPTICAL_SAR
    assert len(result.specialist_results) > 0
    assert result.confidence is None
    
    # Assert neutral language in the deterministic answer (no semantic claims)
    ans = result.answer.lower()
    for term in ["building", "vehicle", "flood", "forest"]:
        assert term not in ans
    
    # Confirm evidence fields are populated
    last_evidence = result.evidence[-1]
    assert last_evidence is not None

def test_engine_invalid_modality(engine, tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    
    sar1_path = str(tmp_path / "sar1.tif")
    sar2_path = str(tmp_path / "sar2.tif")
    
    data = np.ones((2, 100, 100), dtype=np.uint16) * 1000
    transform = from_origin(0, 0, 10, 10)
    
    for path in [sar1_path, sar2_path]:
        with rasterio.open(
            path, 'w', driver='GTiff', height=100, width=100, count=2,
            dtype=data.dtype, crs='+proj=latlong', transform=transform,
        ) as dst:
            dst.write(data)
            
    sar1 = ImageAsset(
        id="1", path=sar1_path, filename="sar1.tif", format="GeoTIFF", 
        modality="sar", crs='+proj=latlong', width=100, height=100, 
        bbox=[0, -1000, 1000, 0]
    )
    sar2 = ImageAsset(
        id="2", path=sar2_path, filename="sar2.tif", format="GeoTIFF", 
        modality="sar", crs='+proj=latlong', width=100, height=100, 
        bbox=[0, -1000, 1000, 0]
    )
    
    bundle = InputBundle(images=[sar1, sar2])
    
    result = engine.analyze(bundle, "fuse optical and sar")
    
    # Due to routing failure in Planner (neither has_optical, nor is_temporal)
    # the planner throws an error.
    assert result.status == "failed"
    assert result.errors[0].code == "PLANNING_FAILED"

def test_engine_spatial_incompatibility(engine, tmp_path):
    opt = ImageAsset(
        id="1", path="fake1.tif", filename="fake1.tif", format="GeoTIFF", 
        modality="optical", crs="+proj=latlong", width=100, height=100, 
        bbox=[0, 0, 10, 10]
    )
    sar = ImageAsset(
        id="2", path="fake2.tif", filename="fake2.tif", format="GeoTIFF", 
        modality="sar", crs="+proj=latlong", width=100, height=100, 
        bbox=[20, 20, 30, 30] # Disjoint
    )
    
    bundle = InputBundle(images=[opt, sar])
    
    result = engine.analyze(bundle, "fuse optical and sar")
    
    assert result.status == "failed"
    assert result.errors[0].code == "INVALID_WORKFLOW"
    assert "No spatial overlap" in result.errors[0].message

def test_engine_deterministic_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("SATQUERY_MODEL_MODE", "real")
    engine_real = SatQueryEngine(registry=ModelRegistry())
    
    import rasterio
    from rasterio.transform import from_origin
    
    opt_path = str(tmp_path / "opt.tif")
    sar_path = str(tmp_path / "sar.tif")
    
    opt_data = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    sar_data = np.ones((2, 100, 100), dtype=np.uint16) * 1000
    
    transform = from_origin(0, 0, 10, 10)
    for path, data in [(opt_path, opt_data), (sar_path, sar_data)]:
        with rasterio.open(
            path, 'w', driver='GTiff', height=100, width=100, count=data.shape[0],
            dtype=data.dtype, crs='+proj=latlong', transform=transform,
        ) as dst:
            dst.write(data)
            
    opt = ImageAsset(
        id="1", path=opt_path, filename="opt.tif", format="GeoTIFF", 
        modality="optical", crs='+proj=latlong', width=100, height=100, 
        bbox=[0, -1000, 1000, 0]
    )
    sar = ImageAsset(
        id="2", path=sar_path, filename="sar.tif", format="GeoTIFF", 
        modality="sar", crs='+proj=latlong', width=100, height=100, 
        bbox=[0, -1000, 1000, 0]
    )
    
    bundle = InputBundle(images=[opt, sar])
    
    result = engine_real.analyze(bundle, "classify this area")
    
    assert result.status == "success"
    
    # Ensure fallback was triggered
    last_evidence = result.evidence[-1] if result.evidence else None
    assert last_evidence is not None
    assert last_evidence.metadata.get("fallback_triggered") == True
    
    # Ensure no fabricated confidence
    assert result.confidence is None

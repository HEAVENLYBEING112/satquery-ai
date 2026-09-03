import pytest
import numpy as np
import os
from engine.core import SatQueryEngine
from engine.contracts import ImageAsset, InputBundle, TaskType, EngineResult, EngineError
from engine.agent.registry import ModelRegistry

@pytest.fixture
def engine():
    return SatQueryEngine()

def create_synthetic_tiff(path, shape, dtype=np.uint16, value=1000):
    import rasterio
    from rasterio.transform import from_origin
    data = np.ones(shape, dtype=dtype) * value
    transform = from_origin(0, 0, 10, 10)
    with rasterio.open(
        path, 'w', driver='GTiff', height=shape[1], width=shape[2], count=shape[0],
        dtype=data.dtype, crs='+proj=latlong', transform=transform,
    ) as dst:
        dst.write(data)
    return path

def test_contract_vqa(engine, tmp_path):
    opt_path = create_synthetic_tiff(str(tmp_path / "opt.tif"), (3, 100, 100))
    img = ImageAsset(id="1", path=opt_path, filename="opt.tif", format="GeoTIFF", modality="optical", width=100, height=100, bbox=[0, -1000, 1000, 0])
    bundle = InputBundle(images=[img])
    
    result = engine.analyze(bundle, "what is in this image?")
    
    assert isinstance(result, EngineResult)
    assert result.status == "success"
    assert result.task == TaskType.SINGLE_IMAGE_VQA
    assert result.answer is not None
    assert isinstance(result.answer, str)
    assert result.confidence is None or isinstance(result.confidence, float)
    
    assert isinstance(result.execution_trace, list)
    assert len(result.execution_trace) > 0

def test_contract_grounding(engine, tmp_path):
    opt_path = create_synthetic_tiff(str(tmp_path / "opt.tif"), (3, 100, 100))
    img = ImageAsset(id="1", path=opt_path, filename="opt.tif", format="GeoTIFF", modality="optical", width=100, height=100, bbox=[0, -1000, 1000, 0])
    bundle = InputBundle(images=[img])
    
    result = engine.analyze(bundle, "highlight buildings")
    
    assert isinstance(result, EngineResult)
    assert result.status == "success"
    assert result.task == TaskType.SINGLE_IMAGE_GROUNDING
    
    # Grounding produces bounding boxes
    assert result.evidence and len(result.evidence) > 0
    last_evidence = result.evidence[-1]
    assert isinstance(last_evidence.bounding_boxes, list)
    
    assert result.confidence is None or isinstance(result.confidence, float)

def test_contract_temporal(engine, tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    
    t1_path = str(tmp_path / "t1.tif")
    t2_path = str(tmp_path / "t2.tif")
    
    data1 = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    data2 = np.ones((3, 100, 100), dtype=np.uint16) * 1000
    data2[:, 40:60, 40:60] = 5000
    
    transform = from_origin(0, 0, 10, 10)
    for path, data in [(t1_path, data1), (t2_path, data2)]:
        with rasterio.open(
            path, 'w', driver='GTiff', height=100, width=100, count=3,
            dtype=data.dtype, crs='+proj=latlong', transform=transform,
        ) as dst:
            dst.write(data)
    
    img1 = ImageAsset(id="1", path=t1_path, filename="t1.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    img2 = ImageAsset(id="2", path=t2_path, filename="t2.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    bundle = InputBundle(images=[img1, img2])
    
    result = engine.analyze(bundle, "what changed?")
    
    assert isinstance(result, EngineResult)
    assert result.status == "success"
    assert result.task in [TaskType.TEMPORAL_CHANGE_DETECTION, TaskType.TEMPORAL_CHANGE_DESCRIPTION, TaskType.TEMPORAL_CHANGE_VQA]
    
    assert result.confidence is None
    
    # Check evidence fields
    last_evidence = result.evidence[-1]
    assert last_evidence.change_statistics is not None
    assert "changed_fraction" in last_evidence.change_statistics
    assert isinstance(last_evidence.bounding_boxes, list)
    
    # The summary is factual
    assert "building" not in str(result.answer).lower()

def test_contract_optical_sar(engine, tmp_path):
    opt_path = create_synthetic_tiff(str(tmp_path / "opt.tif"), (3, 100, 100))
    sar_path = create_synthetic_tiff(str(tmp_path / "sar.tif"), (2, 100, 100))
    
    opt = ImageAsset(id="1", path=opt_path, filename="opt.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    sar = ImageAsset(id="2", path=sar_path, filename="sar.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    bundle = InputBundle(images=[opt, sar])
    
    result = engine.analyze(bundle, "fuse optical and sar")
    
    assert isinstance(result, EngineResult)
    assert result.status == "success"
    assert result.task == TaskType.CROSS_MODAL_OPTICAL_SAR
    assert result.confidence is None
    
    # Neutral language check
    assert "building" not in str(result.answer).lower()

def test_contract_invalid_workflow(engine, tmp_path):
    # Missing required optical image for VQA
    sar_path = create_synthetic_tiff(str(tmp_path / "sar.tif"), (2, 100, 100))
    sar = ImageAsset(id="1", path=sar_path, filename="sar.tif", format="GeoTIFF", modality="sar", width=100, height=100)
    bundle = InputBundle(images=[sar])
    
    result = engine.analyze(bundle, "what is visible?")
    
    assert isinstance(result, EngineResult)
    assert result.status == "failed"
    assert len(result.errors) > 0
    assert isinstance(result.errors[0], EngineError)
    assert result.errors[0].code == "PLANNING_FAILED"

def test_contract_fallback_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("SATQUERY_MODEL_MODE", "real")
    engine_real = SatQueryEngine(registry=ModelRegistry())
    
    opt_path = create_synthetic_tiff(str(tmp_path / "opt.tif"), (3, 100, 100))
    sar_path = create_synthetic_tiff(str(tmp_path / "sar.tif"), (2, 100, 100))
    
    opt = ImageAsset(id="1", path=opt_path, filename="opt.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    sar = ImageAsset(id="2", path=sar_path, filename="sar.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=100, height=100, bbox=[0, -1000, 1000, 0])
    bundle = InputBundle(images=[opt, sar])
    
    result = engine_real.analyze(bundle, "classify this area")
    
    assert result.status == "success"
    last_evidence = result.evidence[-1]
    # Fallback metadata should be visibly distinguishable
    assert last_evidence.metadata.get("fallback_triggered") == True

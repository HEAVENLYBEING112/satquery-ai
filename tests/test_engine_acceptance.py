import pytest
import os
import rasterio
import numpy as np
from rasterio.transform import from_origin
from rasterio.crs import CRS

from engine.core import SatQueryEngine
from engine.contracts import InputBundle, ImageAsset, TaskType
from engine.agent.registry import ModelRegistry

@pytest.fixture
def temp_geotiff(tmp_path):
    def _create(filename, bands, width=20, height=20, offset=0):
        filepath = tmp_path / filename
        transform = from_origin(10.0 + offset, 20.0 + offset, 10.0, 10.0)
        profile = {
            'driver': 'GTiff',
            'height': height,
            'width': width,
            'count': bands,
            'dtype': 'uint8',
            'crs': CRS.from_epsg(4326),
            'transform': transform
        }
        with rasterio.open(filepath, 'w', **profile) as dst:
            for b in range(1, bands + 1):
                dst.write(np.full((height, width), b * 10, dtype='uint8'), b)
        return str(filepath)
    return _create

@pytest.fixture
def engine():
    os.environ["SATQUERY_MODEL_MODE"] = "mock"
    return SatQueryEngine(registry=ModelRegistry())

def test_e01_single_image_vqa(engine, temp_geotiff):
    path = temp_geotiff("opt.tif", 3)
    img = ImageAsset(id="1", path=path, filename="opt.tif", format="GeoTIFF", modality="optical", width=20, height=20)
    bundle = InputBundle(images=[img])
    result = engine.analyze(bundle, "What is visible?")
    
    assert result.status == "success"
    assert result.task == TaskType.SINGLE_IMAGE_VQA
    assert result.confidence is None

def test_e02_single_image_grounding(engine, temp_geotiff):
    path = temp_geotiff("opt.tif", 3)
    img = ImageAsset(id="1", path=path, filename="opt.tif", format="GeoTIFF", modality="optical", width=20, height=20)
    bundle = InputBundle(images=[img])
    result = engine.analyze(bundle, "Highlight the water")
    
    assert result.status == "success"
    assert result.task == TaskType.SINGLE_IMAGE_GROUNDING

def test_e03_temporal_change_detection(engine, temp_geotiff):
    path1 = temp_geotiff("t1.tif", 3)
    path2 = temp_geotiff("t2.tif", 3)
    img1 = ImageAsset(id="1", path=path1, filename="t1.tif", format="GeoTIFF", modality="optical", width=20, height=20)
    img2 = ImageAsset(id="2", path=path2, filename="t2.tif", format="GeoTIFF", modality="optical", width=20, height=20)
    bundle = InputBundle(images=[img1, img2])
    result = engine.analyze(bundle, "What changed between these two dates?")
    
    assert result.status == "success"
    assert result.task in [TaskType.TEMPORAL_CHANGE_DETECTION, TaskType.TEMPORAL_CHANGE_DESCRIPTION, TaskType.TEMPORAL_CHANGE_VQA]

def test_e08_invalid_cross_modal_input(engine, temp_geotiff):
    path1 = temp_geotiff("opt1.tif", 3)
    img1 = ImageAsset(id="1", path=path1, filename="opt1.tif", format="GeoTIFF", modality="optical", width=20, height=20)
    bundle = InputBundle(images=[img1])
    # Force cross-modal with 1 image
    result = engine.analyze(bundle, "Use SAR and optical to classify.")
    
    # It might fall back to SINGLE_IMAGE_VQA or fail.
    # If it fails, that's fine. If it succeeds, it must not be CROSS_MODAL.
    if result.status == "failed":
        pass
    else:
        assert result.task != TaskType.CROSS_MODAL_OPTICAL_SAR

def test_e11_missing_croma(engine, temp_geotiff, monkeypatch):
    monkeypatch.setenv("SATQUERY_MODEL_MODE", "real")
    engine_real = SatQueryEngine(registry=ModelRegistry())
    
    path1 = temp_geotiff("opt1.tif", 12)
    path2 = temp_geotiff("sar1.tif", 2)
    img1 = ImageAsset(id="1", path=path1, filename="opt1.tif", format="GeoTIFF", modality="optical", width=20, height=20)
    img2 = ImageAsset(id="2", path=path2, filename="sar1.tif", format="GeoTIFF", modality="sar", width=20, height=20)
    bundle = InputBundle(images=[img1, img2])
    
    result = engine_real.analyze(bundle, "Use SAR and optical to classify.")
    
    assert result.status == "success"
    # evidence is a list of EvidenceBundle. The last one is the final output.
    last_evidence = result.evidence[-1] if result.evidence else None
    assert last_evidence is not None
    assert last_evidence.metadata.get("fallback_triggered") == True

def test_e18_execution_trace(engine, temp_geotiff):
    path = temp_geotiff("opt.tif", 3)
    img = ImageAsset(id="1", path=path, filename="opt.tif", format="GeoTIFF", modality="optical", width=20, height=20)
    bundle = InputBundle(images=[img])
    result = engine.analyze(bundle, "What is visible?")
    
    assert result.execution_trace is not None
    assert len(result.execution_trace) > 0
    assert "duration_ms" in result.execution_trace[0]

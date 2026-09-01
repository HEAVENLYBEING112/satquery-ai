import os
import pytest
import numpy as np
from engine.contracts import InputBundle, ImageAsset, TaskType, WorkflowStep
from engine.models.optical_sar_ai import OpticalSARAI
import rasterio
from rasterio.transform import from_origin

@pytest.fixture
def opt_img(tmp_path):
    p = str(tmp_path / "opt.tif")
    data = np.ones((3, 10, 10), dtype=np.uint8) * 100
    transform = from_origin(0, 0, 10, 10)
    with rasterio.open(p, 'w', driver='GTiff', height=10, width=10, count=3, dtype=data.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(data)
    return ImageAsset(id="opt1", path=p, filename="opt.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=10, height=10, bbox=[0, -100, 100, 0])

@pytest.fixture
def sar_img(tmp_path):
    p = str(tmp_path / "sar.tif")
    data = np.ones((1, 10, 10), dtype=np.float32) * 10
    transform = from_origin(0, 0, 10, 10)
    with rasterio.open(p, 'w', driver='GTiff', height=10, width=10, count=1, dtype=data.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(data)
    return ImageAsset(id="sar1", path=p, filename="sar.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=10, height=10, bbox=[0, -100, 100, 0])

def test_optical_sar_ai_initialization():
    model = OpticalSARAI()
    assert model.name == "OpticalSARAI_DualEncoder"
    assert TaskType.CROSS_MODAL_OPTICAL_SAR in model.supported_tasks

def test_optical_sar_ai_lazy_loading(opt_img, sar_img):
    model = OpticalSARAI()
    
    # We don't want to enforce torch installation for all CI runs if it's a fallback environment
    try:
        import torch
    except ImportError:
        pytest.skip("PyTorch not available for AI execution.")
        
    bundle = InputBundle(images=[opt_img, sar_img])
    step = WorkflowStep(tool="OpticalSARAI_DualEncoder")
    
    # Run should trigger lazy load
    result = model.run(bundle, step, "Test cross-modal fusion")
    assert result.status == "success"
    assert "dual-encoder" in result.evidence.textual_evidence
    assert "optical" in result.evidence.metadata["modalities_used"]
    assert "sar" in result.evidence.metadata["modalities_used"]

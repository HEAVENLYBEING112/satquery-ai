import os
import pytest
import numpy as np
import rasterio
from rasterio.transform import from_origin

from engine.contracts import InputBundle, ImageAsset, TaskType, WorkflowStep
from engine.models.croma import CROMASpecialist

@pytest.fixture
def croma_fixtures(tmp_path):
    opt_path = str(tmp_path / "opt.tif")
    sar_path = str(tmp_path / "sar.tif")
    transform = from_origin(0, 0, 10, 10)
    
    # Valid sizes
    opt_arr = np.ones((12, 120, 120), dtype=np.float32)
    sar_arr = np.ones((2, 120, 120), dtype=np.float32)
    
    with rasterio.open(opt_path, 'w', driver='GTiff', height=120, width=120, count=12, dtype=opt_arr.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(opt_arr)
    with rasterio.open(sar_path, 'w', driver='GTiff', height=120, width=120, count=2, dtype=sar_arr.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(sar_arr)
        
    opt = ImageAsset(id="opt", path=opt_path, filename="opt.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=120, height=120, bbox=[0, -100, 100, 0])
    sar = ImageAsset(id="sar", path=sar_path, filename="sar.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=120, height=120, bbox=[0, -100, 100, 0])
    
    return InputBundle(images=[opt, sar])

@pytest.fixture
def invalid_band_fixtures(tmp_path):
    opt_path = str(tmp_path / "opt_inv.tif")
    sar_path = str(tmp_path / "sar_inv.tif")
    transform = from_origin(0, 0, 10, 10)
    
    # Invalid sizes (3 bands instead of 12)
    opt_arr = np.ones((3, 120, 120), dtype=np.float32)
    sar_arr = np.ones((1, 120, 120), dtype=np.float32)
    
    with rasterio.open(opt_path, 'w', driver='GTiff', height=120, width=120, count=3, dtype=opt_arr.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(opt_arr)
    with rasterio.open(sar_path, 'w', driver='GTiff', height=120, width=120, count=1, dtype=sar_arr.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(sar_arr)
        
    opt = ImageAsset(id="opt", path=opt_path, filename="opt_inv.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=120, height=120, bbox=[0, -100, 100, 0])
    sar = ImageAsset(id="sar", path=sar_path, filename="sar_inv.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=120, height=120, bbox=[0, -100, 100, 0])
    
    return InputBundle(images=[opt, sar])

def test_croma_can_run(croma_fixtures):
    croma = CROMASpecialist()
    assert croma.can_run(croma_fixtures, TaskType.CROSS_MODAL_OPTICAL_SAR)
    assert not croma.can_run(croma_fixtures, TaskType.SINGLE_IMAGE_VQA)

def test_croma_invalid_bands(invalid_band_fixtures):
    croma = CROMASpecialist()
    step = WorkflowStep(tool="croma_specialist")
    
    # We set hardware_unavailable to False manually to test the band validation logic
    # instead of the hardware fallback logic
    croma._hardware_unavailable = False
    
    # Mock lazy load to do nothing and succeed
    def mock_lazy_load():
        croma._is_loaded = True
    croma._lazy_load_model = mock_lazy_load
    
    result = croma.run(invalid_band_fixtures, step, "test")
    assert result.status == "error"
    assert "12-band" in result.error

def test_croma_fallback(croma_fixtures):
    croma = CROMASpecialist()
    step = WorkflowStep(tool="croma_specialist")
    
    # Force hardware unavailable
    croma._hardware_unavailable = True
    
    result = croma.run(croma_fixtures, step, "test")
    
    # Should succeed via fallback
    assert result.status == "success"
    assert result.metadata.get("fallback_triggered") is True
    assert result.model_name == "optical_sar_specialist"

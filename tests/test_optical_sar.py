import os
import pytest
import numpy as np
import rasterio
from rasterio.transform import from_origin
from engine.contracts import InputBundle, ImageAsset, TaskType, WorkflowPlan, WorkflowStep
from engine.agent.planner import Planner, PlannerError
from engine.agent.executor import WorkflowExecutor
from engine.agent.registry import registry
from engine.evidence.validator import PlanValidator, ValidationError

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

def test_planner_routes_optical_sar_correctly(opt_img, sar_img):
    planner = Planner()
    bundle = InputBundle(images=[opt_img, sar_img])
    
    plan = planner.plan("Use both optical and SAR to find water", bundle)
    assert plan.task == TaskType.CROSS_MODAL_OPTICAL_SAR
    assert len(plan.steps) == 1
    assert plan.steps[0].tool == "optical_sar_specialist"

def test_planner_distinguishes_temporal_vs_cross_modal(opt_img, tmp_path):
    opt_img2 = ImageAsset(id="opt2", path=str(tmp_path / "opt2.tif"), filename="opt2.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=10, height=10, bbox=[0, -100, 100, 0])
    planner = Planner()
    
    # Temporal optical
    bundle_temp = InputBundle(images=[opt_img, opt_img2])
    plan_temp = planner.plan("What changed between these dates", bundle_temp)
    assert plan_temp.task in [TaskType.TEMPORAL_CHANGE_DETECTION, TaskType.TEMPORAL_CHANGE_VQA, TaskType.TEMPORAL_CHANGE_DESCRIPTION]

def test_validator_rejects_invalid_pairs(opt_img, sar_img, tmp_path):
    validator = PlanValidator()
    planner = Planner()
    
    # Valid Optical + SAR
    bundle_valid = InputBundle(images=[opt_img, sar_img])
    plan_valid = planner.plan("Use both", bundle_valid)
    assert validator.validate(plan_valid, bundle_valid) is True
    
    # Wrong pair: Optical + Optical for Cross-Modal task manually created
    opt_img2 = ImageAsset(id="opt2", path="opt2.tif", filename="opt2.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=10, height=10, bbox=[0, -100, 100, 0])
    bundle_opt_opt = InputBundle(images=[opt_img, opt_img2])
    plan_invalid = WorkflowPlan(task=TaskType.CROSS_MODAL_OPTICAL_SAR, input_type=bundle_opt_opt.determine_input_type(), input_ids=["opt1", "opt2"], steps=[WorkflowStep(tool="dummy")], planner_source="test")
    with pytest.raises(ValidationError, match="Optical-SAR analysis requires at least one optical and one SAR image"):
        validator.validate(plan_invalid, bundle_opt_opt)
        
    # No overlap
    sar_no_overlap = ImageAsset(id="sar2", path=sar_img.path, filename="sar2.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=10, height=10, bbox=[1000, 1000, 2000, 2000])
    bundle_no_overlap = InputBundle(images=[opt_img, sar_no_overlap])
    plan_no_overlap = planner.plan("Use both", bundle_no_overlap)
    with pytest.raises(ValidationError, match="No spatial overlap"):
        validator.validate(plan_no_overlap, bundle_no_overlap)

def test_optical_sar_execution_e2e(opt_img, sar_img):
    executor = WorkflowExecutor(registry)
    planner = Planner()
    
    bundle = InputBundle(images=[opt_img, sar_img])
    plan = planner.plan("Use both optical and SAR to identify built-up and water-covered regions.", bundle)
    
    result = executor.execute(plan, "Use both optical and SAR to identify built-up and water-covered regions.", bundle)
    assert result.status == "success"
    assert result.task == TaskType.CROSS_MODAL_OPTICAL_SAR
    assert len(result.specialist_results) == 1
    
    spec_result = result.specialist_results[0]
    assert "modality_usage" in spec_result.metadata
    assert "optical" in spec_result.metadata["modality_usage"]
    assert "sar" in spec_result.metadata["modality_usage"]
    
    evidence = spec_result.evidence
    assert evidence.bounding_boxes is not None
    assert evidence.visualizations is not None
    assert "water_agreement_pixels" in evidence.metadata

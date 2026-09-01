import os
import sys
import numpy as np
import rasterio
from rasterio.transform import from_origin

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.contracts import ImageAsset, InputBundle, TaskType, WorkflowStep
from engine.agent.registry import registry
from engine.models.optical_sar import OpticalSARSpecialist
from engine.models.optical_sar_ai import OpticalSARAI

def create_synthetic_fixtures():
    os.makedirs("tests/fixtures", exist_ok=True)
    
    # Create Optical
    opt_path = "tests/fixtures/crossmodal_optical.tif"
    if not os.path.exists(opt_path):
        data = np.ones((3, 64, 64), dtype=np.uint8) * 100
        # Add a fake "built-up" region
        data[:, 10:30, 10:30] = 200 
        transform = from_origin(0, 0, 10, 10)
        with rasterio.open(opt_path, 'w', driver='GTiff', height=64, width=64, count=3, dtype=data.dtype, crs='+proj=latlong', transform=transform) as dst:
            dst.write(data)
            
    # Create SAR
    sar_path = "tests/fixtures/crossmodal_sar.tif"
    if not os.path.exists(sar_path):
        data = np.ones((1, 64, 64), dtype=np.float32) * 5.0
        # Add fake high backscatter
        data[0, 10:30, 10:30] = 50.0 
        transform = from_origin(0, 0, 10, 10)
        with rasterio.open(sar_path, 'w', driver='GTiff', height=64, width=64, count=1, dtype=data.dtype, crs='+proj=latlong', transform=transform) as dst:
            dst.write(data)
            
    opt = ImageAsset(id="opt", path=opt_path, filename="crossmodal_optical.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=64, height=64, bbox=[0, -100, 100, 0])
    sar = ImageAsset(id="sar", path=sar_path, filename="crossmodal_sar.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=64, height=64, bbox=[0, -100, 100, 0])
    
    return InputBundle(images=[opt, sar])

def evaluate_model(name, model, bundle):
    print(f"\nEvaluating {name}...")
    step = WorkflowStep(tool=model.name)
    result = model.run(bundle, step, "Evaluate dual-modality areas.")
    
    print(f"Status: {result.status}")
    if result.status == "success":
        print(f"Answer: {result.answer}")
        print(f"BBoxes: {len(result.evidence.bounding_boxes)}")
        if 'modalities_used' in result.evidence.metadata:
            print(f"Modalities used: {result.evidence.metadata['modalities_used']}")
    else:
        print(f"Error: {result.error}")

if __name__ == "__main__":
    print("--- Optical-SAR Evaluation ---")
    print("Dataset: synthetic validation")
    
    bundle = create_synthetic_fixtures()
    
    # 1. Baseline
    baseline = OpticalSARSpecialist()
    evaluate_model("OpticalSARBaseline", baseline, bundle)
    
    # 2. AI
    ai = OpticalSARAI()
    evaluate_model("OpticalSARAI", ai, bundle)

import os
import sys
import argparse
import numpy as np
import rasterio
from rasterio.transform import from_origin

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.contracts import ImageAsset, InputBundle, TaskType, WorkflowStep
from engine.models.croma import CROMASpecialist

def create_synthetic_fixtures():
    os.makedirs("tests/fixtures", exist_ok=True)
    opt_path = "tests/fixtures/croma_opt.tif"
    sar_path = "tests/fixtures/croma_sar.tif"
    
    transform = from_origin(0, 0, 10, 10)
    opt_arr = np.random.rand(12, 120, 120).astype(np.float32)
    sar_arr = np.random.rand(2, 120, 120).astype(np.float32)
    
    with rasterio.open(opt_path, 'w', driver='GTiff', height=120, width=120, count=12, dtype=opt_arr.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(opt_arr)
    with rasterio.open(sar_path, 'w', driver='GTiff', height=120, width=120, count=2, dtype=sar_arr.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(sar_arr)
        
    opt = ImageAsset(id="opt", path=opt_path, filename="croma_opt.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=120, height=120, bbox=[0, -100, 100, 0])
    sar = ImageAsset(id="sar", path=sar_path, filename="croma_sar.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=120, height=120, bbox=[0, -100, 100, 0])
    
    return InputBundle(images=[opt, sar])

def run_smoke_test(is_real=False):
    print(f"--- CROMA Classifier Smoke Test ({'REAL' if is_real else 'SYNTHETIC'} MODE) ---")
    
    if is_real:
        print("[PENDING DATA] Real mode requires authentic co-registered Sentinel-1/Sentinel-2 imagery.")
        print("Falling back to synthetic fixture test for pipeline validation.")
        
    bundle = create_synthetic_fixtures()
    croma = CROMASpecialist()
    
    print("Executing CROMASpecialist (with downstream classifier check)...")
    step = WorkflowStep(tool="croma_specialist")
    result = croma.run(bundle, step, "Classify this area.")
    
    print("\n--- Result ---")
    print(f"Status: {result.status}")
    if result.status == "success" and not result.metadata.get("fallback_triggered"):
        ev_meta = result.evidence.metadata
        print(f"Model: {ev_meta.get('model')}")
        print(f"Device: {ev_meta.get('device')}")
        print(f"Input: 2-channel SAR + 12-channel optical")
        print(f"Joint embedding shape: {ev_meta.get('embedding_shape')}")
        print(f"Head trained: {ev_meta.get('head_trained')}")
        print(f"Predicted class: {ev_meta.get('predicted_class')}")
        print(f"Runtime: {result.execution_time:.3f}s")
        print("Status: SUCCESS")
        print(f"Answer: {result.answer}")
    elif result.status == "success" and result.metadata.get("fallback_triggered"):
        print(f"Status: FALLBACK TRIGGERED (Hardware/Weights unavailable)")
        print(f"Reason: {result.metadata.get('fallback_reason')}")
        print(f"Fallback Model: {result.model_name}")
    else:
        print(f"Status: ERROR")
        print(f"Error: {result.error}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Run with real data")
    args = parser.parse_args()
    
    run_smoke_test(is_real=args.real)

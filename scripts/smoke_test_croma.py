import os
import sys
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.contracts import ImageAsset, InputBundle, TaskType, WorkflowStep
from engine.models.croma import CROMASpecialist

def run_synthetic_smoke_test():
    print("--- CROMA Synthetic Tensor Smoke Test ---")
    
    # Create valid 12-channel Sentinel-2 optical tensor
    print("Constructing 12-channel Sentinel-2 synthetic tensor...")
    opt_arr = np.random.rand(12, 120, 120).astype(np.float32)
    
    # Create valid 2-channel Sentinel-1 SAR tensor
    print("Constructing 2-channel Sentinel-1 synthetic tensor...")
    sar_arr = np.random.rand(2, 120, 120).astype(np.float32)
    
    import rasterio
    from rasterio.transform import from_origin
    os.makedirs("tests/fixtures", exist_ok=True)
    
    opt_path = "tests/fixtures/croma_opt.tif"
    sar_path = "tests/fixtures/croma_sar.tif"
    transform = from_origin(0, 0, 10, 10)
    
    with rasterio.open(opt_path, 'w', driver='GTiff', height=120, width=120, count=12, dtype=opt_arr.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(opt_arr)
        
    with rasterio.open(sar_path, 'w', driver='GTiff', height=120, width=120, count=2, dtype=sar_arr.dtype, crs='+proj=latlong', transform=transform) as dst:
        dst.write(sar_arr)
    
    opt = ImageAsset(id="opt", path=opt_path, filename="croma_opt.tif", format="GeoTIFF", modality="optical", crs='+proj=latlong', width=120, height=120, bbox=[0, -100, 100, 0])
    sar = ImageAsset(id="sar", path=sar_path, filename="croma_sar.tif", format="GeoTIFF", modality="sar", crs='+proj=latlong', width=120, height=120, bbox=[0, -100, 100, 0])
    
    bundle = InputBundle(images=[opt, sar])
    
    # Run
    croma = CROMASpecialist()
    print("Executing CROMASpecialist...")
    
    step = WorkflowStep(tool="croma_specialist")
    result = croma.run(bundle, step, "Extract joint embedding")
    
    print("\n--- Result ---")
    print(f"Status: {result.status}")
    if result.status == "success" and not result.metadata.get("fallback_triggered"):
        print(f"Model: CROMA-base")
        print(f"Input: 2-channel SAR + 12-channel optical")
        print(f"Joint embedding shape: {result.evidence.metadata.get('embedding_shape')}")
        print(f"Runtime: {result.execution_time:.3f}s")
        print(f"Device: {result.evidence.metadata.get('device')}")
        print("Status: SUCCESS")
    elif result.status == "success" and result.metadata.get("fallback_triggered"):
        print(f"Status: DEPENDENCY_UNAVAILABLE / HARDWARE_UNAVAILABLE (Fallback triggered)")
        print(f"Reason: {result.metadata.get('fallback_reason')}")
        print(f"Fallback Model: {result.model_name}")
    else:
        print(f"Status: ERROR")
        print(f"Error: {result.error}")

if __name__ == "__main__":
    run_synthetic_smoke_test()

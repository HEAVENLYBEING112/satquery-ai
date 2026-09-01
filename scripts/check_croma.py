import sys
import os

def check_croma_environment():
    print("--- CROMA Environment Check ---")
    
    # 1. Check Torch
    has_torch = False
    has_cuda = False
    try:
        import torch
        has_torch = True
        has_cuda = torch.cuda.is_available()
        print(f"Torch: AVAILABLE (v{torch.__version__})")
        print(f"CUDA: {'AVAILABLE' if has_cuda else 'UNAVAILABLE'}")
        print(f"Device: {'CUDA' if has_cuda else 'CPU'}")
    except ImportError:
        print("Torch: UNAVAILABLE")
        print("CUDA: UNAVAILABLE")
        print("Device: None")
        
    # 2. Check Einops
    try:
        import einops
        print(f"Einops: AVAILABLE (v{einops.__version__})")
    except ImportError:
        print("Einops: UNAVAILABLE")
        
    # 3. Check Transformers
    has_transformers = False
    try:
        import transformers
        has_transformers = True
        print(f"Transformers: AVAILABLE (v{transformers.__version__})")
    except ImportError:
        print("Transformers: UNAVAILABLE")
        
    # 4. Check CROMA Weights availability locally
    print("\nAttempting to locate CROMA weights...")
    if has_torch and has_transformers:
        try:
            from transformers import AutoModel
            print("Testing AutoModel.from_pretrained('BiliSakura/CROMA-transformers', trust_remote_code=True)...")
            # We use local_files_only=True to see if it's cached. If it fails, weights are not found locally.
            try:
                model = AutoModel.from_pretrained("BiliSakura/CROMA-transformers", trust_remote_code=True, local_files_only=True)
                print("Weights: FOUND (Cached locally)")
                print("CROMA: AVAILABLE")
            except Exception as e:
                print("Weights: NOT FOUND (Not cached locally)")
                print("CROMA: UNAVAILABLE (Requires download)")
                print(f"Detail: {e}")
        except Exception as e:
            print(f"CROMA: UNAVAILABLE (Error: {e})")
    else:
        print("Weights: NOT FOUND (Dependencies missing)")
        print("CROMA: UNAVAILABLE")
        
if __name__ == "__main__":
    check_croma_environment()

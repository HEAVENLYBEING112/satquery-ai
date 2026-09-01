import os
import sys

def check_hardware():
    print("==================================================")
    print("SATQUERY HARDWARE CHECK")
    print("==================================================")
    
    try:
        import torch
        print(f"Torch Version: {torch.__version__}")
        
        has_cuda = torch.cuda.is_available()
        print(f"CUDA Available: {has_cuda}")
        
        if has_cuda:
            print(f"GPU Name: {torch.cuda.get_device_name(0)}")
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            print(f"Total VRAM: {vram_bytes / (1024**3):.2f} GB")
        else:
            print("GPU Name: N/A")
            print("Total VRAM: N/A")
    except ImportError:
        print("Torch: NOT INSTALLED")
        
    print("-" * 50)
    
    try:
        import transformers
        print(f"Transformers Version: {transformers.__version__}")
    except ImportError:
        print("Transformers: NOT INSTALLED")
        
    print("-" * 50)
    
    # Check CROMA availability (using safe AutoModel probe with local_files_only)
    try:
        from transformers import AutoModel
        import torch
        print("Testing CROMA availability from local cache...")
        try:
            model = AutoModel.from_pretrained("BiliSakura/CROMA-transformers", trust_remote_code=True, local_files_only=True)
            print("CROMA Weights: AVAILABLE (cached)")
        except Exception as e:
            print("CROMA Weights: UNAVAILABLE (requires download)")
    except ImportError:
        print("CROMA Weights: UNAVAILABLE (dependencies missing)")
        
    print("==================================================")

if __name__ == "__main__":
    check_hardware()

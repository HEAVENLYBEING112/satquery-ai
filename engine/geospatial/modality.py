from typing import Optional

def detect_modality(filename: str, band_count: int, metadata: dict) -> str:
    """Safely detects modality based on structural constraints first, falling back to heuristics."""
    # 1. Explicit metadata if provided (e.g., from frontend or API)
    if metadata and "modality" in metadata:
        return metadata["modality"].lower()
        
    fn_lower = filename.lower()
    
    # 2. Structural/Band characteristics (Defensible)
    if band_count == 3:
        return "optical"
    if band_count > 3:
        return "multispectral"
        
    # 3. Filename heuristic ONLY as a documented fallback for 1-2 band images
    if band_count in [1, 2]:
        if "sar" in fn_lower or "s1" in fn_lower:
            return "sar"
        if "optical" in fn_lower or "s2" in fn_lower or "rgb" in fn_lower:
            return "optical"
            
    # 4. Otherwise UNKNOWN (do not silently classify as SAR)
    return "unknown"

from typing import Optional

def detect_modality(filename: str, band_count: int, metadata: dict) -> str:
    """Heuristic modality detection."""
    fn_lower = filename.lower()
    
    # Explicit hints in filename
    if "sar" in fn_lower or "s1" in fn_lower:
        return "sar"
    if "optical" in fn_lower or "s2" in fn_lower or "rgb" in fn_lower:
        if band_count > 3:
            return "multispectral"
        return "optical"
        
    # Band count heuristics
    if band_count == 1:
        # Could be SAR, single-band optical, mask, etc.
        return "unknown"
    if band_count == 3:
        return "optical"
    if band_count > 3:
        return "multispectral"
        
    return "unknown"

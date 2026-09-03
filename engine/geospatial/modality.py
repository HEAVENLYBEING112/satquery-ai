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
        
    # 3. We no longer use filename heuristics as scientific proof for ambiguous 1/2-band data.
    # Without explicit metadata, 1/2-band imagery is structurally ambiguous (could be panchromatic, mask, SAR).
    return "unknown"

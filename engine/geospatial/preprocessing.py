import numpy as np

def optical_preprocess(array: np.ndarray, nodata: float = None) -> np.ndarray:
    """
    Robust optical percentile normalization.
    Assuming array shape is (bands, height, width).
    Returns normalized float array in range [0, 1].
    """
    if len(array.shape) != 3:
        raise ValueError("Optical array must be 3D (bands, height, width)")
        
    out = np.zeros_like(array, dtype=np.float32)
    for b in range(array.shape[0]):
        band = array[b].astype(np.float32)
        if nodata is not None:
            valid_mask = band != nodata
        else:
            valid_mask = np.ones_like(band, dtype=bool)
            
        if np.any(valid_mask):
            valid_pixels = band[valid_mask]
            p2, p98 = np.percentile(valid_pixels, (2, 98))
            
            # Avoid division by zero
            if p98 > p2:
                norm = (band - p2) / (p98 - p2)
                norm = np.clip(norm, 0, 1)
            else:
                norm = np.zeros_like(band)
            
            out[b][valid_mask] = norm[valid_mask]
            
    return out

def sar_preprocess(array: np.ndarray, nodata: float = None, is_db: bool = False) -> np.ndarray:
    """
    SAR specific preprocessing.
    If the array is not in dB, we convert it to dB first (assuming linear amplitude/power).
    Then normalize based on common dB ranges for backscatter.
    """
    if len(array.shape) != 3:
        raise ValueError("SAR array must be 3D (bands, height, width)")
        
    out = np.zeros_like(array, dtype=np.float32)
    for b in range(array.shape[0]):
        band = array[b].astype(np.float32)
        if nodata is not None:
            valid_mask = band != nodata
            # SAR can have <= 0 values if linear
            valid_mask = valid_mask & (band > 0) if not is_db else valid_mask
        else:
            valid_mask = band > 0 if not is_db else np.ones_like(band, dtype=bool)
            
        if np.any(valid_mask):
            valid_pixels = band[valid_mask]
            
            if not is_db:
                # Convert linear power/amplitude to dB
                # We assume power here. If amplitude, it should be 20 * log10. 
                # Let's just use 10 * log10 as a standard backscatter representation
                db_pixels = 10 * np.log10(valid_pixels + 1e-10)
                band[valid_mask] = db_pixels
                
            # Normalize dB to [0, 1] using typical SAR ranges [-30, 0] dB
            # Instead of strict fixed min/max, we can use percentiles for robustness
            db_valid = band[valid_mask]
            p2, p98 = np.percentile(db_valid, (2, 98))
            
            if p98 > p2:
                norm = (band - p2) / (p98 - p2)
                norm = np.clip(norm, 0, 1)
            else:
                norm = np.zeros_like(band)
                
            out[b][valid_mask] = norm[valid_mask]
            
    return out

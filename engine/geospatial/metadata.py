from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class BandInfo:
    index: int
    dtype: str
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    
def extract_band_stats(data: Any, index: int, sample_size: Optional[int] = None) -> BandInfo:
    """Helper to extract statistics from a band, optionally sampling to save memory."""
    import numpy as np
    
    if data is None:
        return BandInfo(index=index, dtype="unknown")
        
    flat = data.flatten()
    if sample_size and len(flat) > sample_size:
        flat = np.random.choice(flat, size=sample_size, replace=False)
        
    return BandInfo(
        index=index,
        dtype=str(data.dtype),
        minimum=float(np.min(flat)),
        maximum=float(np.max(flat)),
        mean=float(np.mean(flat)),
        std=float(np.std(flat))
    )

from typing import Any
import numpy as np

class PreprocessingError(Exception):
    pass

class BasePreprocessor:
    def process(self, data: Any, metadata: dict) -> Any:
        raise NotImplementedError

class OpticalPreprocessor(BasePreprocessor):
    def process(self, data: np.ndarray, metadata: dict) -> np.ndarray:
        # Example interface: Handle nodata, select bands, normalize
        nodata = metadata.get("nodata")
        if nodata is not None:
            data = np.where(data == nodata, 0, data)
        return data

class SARPreprocessor(BasePreprocessor):
    def process(self, data: np.ndarray, metadata: dict) -> np.ndarray:
        # Example interface: SAR log transform, speckle filtering, etc.
        nodata = metadata.get("nodata")
        if nodata is not None:
            data = np.where(data == nodata, 1e-6, data)
        # Avoid log of zero/negative
        data = np.where(data <= 0, 1e-6, data)
        return 10 * np.log10(data)

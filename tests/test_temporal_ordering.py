import pytest
from engine.contracts import ImageAsset, InputBundle

def test_temporal_ordering_by_acquisition_time():
    img1 = ImageAsset(id="1", path="a.tif", filename="a", format="GeoTIFF", modality="optical", acquisition_time="2022-01-01T00:00:00Z")
    img2 = ImageAsset(id="2", path="b.tif", filename="b", format="GeoTIFF", modality="optical", acquisition_time="2021-01-01T00:00:00Z")
    
    # Even though img1 is first in the list, img2 is older
    bundle = InputBundle(images=[img1, img2])
    
    assert bundle.before.id == "2"
    assert bundle.after.id == "1"

def test_temporal_ordering_fallback():
    img1 = ImageAsset(id="1", path="a.tif", filename="a", format="GeoTIFF", modality="optical")
    img2 = ImageAsset(id="2", path="b.tif", filename="b", format="GeoTIFF", modality="optical")
    
    # No timestamps, falls back to input order
    bundle = InputBundle(images=[img1, img2])
    
    assert bundle.before.id == "1"
    assert bundle.after.id == "2"

import pytest
from engine.contracts import ImageAsset
from engine.geospatial.registration import register_pair

def test_registration_identity():
    # Same CRS, bounds, dims -> NOT_REQUIRED
    before = ImageAsset(
        id="1", path="a.tif", filename="a", format="GeoTIFF", modality="optical",
        crs="EPSG:4326", width=256, height=256, bbox=[0, 0, 10, 10]
    )
    after = ImageAsset(
        id="2", path="b.tif", filename="b", format="GeoTIFF", modality="optical",
        crs="EPSG:4326", width=256, height=256, bbox=[0, 0, 10, 10]
    )
    
    result = register_pair(before, after)
    assert result.status == "NOT_REQUIRED"
    assert result.aligned_before_path == "a.tif"
    assert result.aligned_after_path == "b.tif"

def test_registration_incompatible_crs():
    # Missing CRS
    before = ImageAsset(
        id="1", path="a.tif", filename="a", format="GeoTIFF", modality="optical",
        crs=None, width=256, height=256
    )
    after = ImageAsset(
        id="2", path="b.tif", filename="b", format="GeoTIFF", modality="optical",
        crs=None, width=256, height=256
    )
    
    # Missing CRS will fallback to rasterio opening the file to see if it has CRS, but path doesn't exist
    # So it should throw an error which is caught and returns INCOMPATIBLE
    result = register_pair(before, after)
    assert result.status == "INCOMPATIBLE"

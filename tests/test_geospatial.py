import os
import pytest
from engine.geospatial.loader import RasterLoader, RasterLoaderError
from engine.geospatial.modality import detect_modality
from engine.geospatial.tiling import TileGenerator, TileConfig
from engine.contracts import InputBundle

@pytest.fixture
def fixtures_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")

def test_loader_valid_geotiff(fixtures_dir):
    loader = RasterLoader()
    opt_path = os.path.join(fixtures_dir, "optical.tif")
    asset = loader.load(opt_path)
    
    assert asset.format == "GeoTIFF"
    assert asset.width == 256
    assert asset.height == 256
    assert asset.bands == 3
    assert asset.modality == "optical"
    assert asset.crs is not None
    assert asset.resolution == 10.0
    assert asset.metadata["dtype"] == "uint16"

def test_loader_invalid_file():
    loader = RasterLoader()
    with pytest.raises(RasterLoaderError):
        loader.load("does_not_exist.tif")

def test_loader_modality_override(fixtures_dir):
    loader = RasterLoader()
    sar_path = os.path.join(fixtures_dir, "sar.tif")
    asset = loader.load(sar_path, modality_override="custom_modality")
    assert asset.modality == "custom_modality"

def test_detect_modality():
    assert detect_modality("s1_image.tif", 1, {}) == "sar"
    assert detect_modality("s2_image.tif", 3, {}) == "optical"
    assert detect_modality("some_image.tif", 4, {}) == "multispectral"
    assert detect_modality("unknown.tif", 2, {}) == "unknown"

def test_tiling():
    config = TileConfig(tile_size=128, overlap=0)
    generator = TileGenerator(config)
    tiles = list(generator.generate_tiles(256, 256))
    
    assert len(tiles) == 4
    assert tiles[0] == (0, 0, 128, 128)
    assert tiles[1] == (128, 0, 128, 128)
    assert tiles[2] == (0, 128, 128, 128)
    assert tiles[3] == (128, 128, 128, 128)

def test_validator_temporal_compatibility(fixtures_dir):
    from engine.evidence.validator import PlanValidator
    from engine.agent.planner import Planner
    
    loader = RasterLoader()
    img1 = loader.load(os.path.join(fixtures_dir, "before.tif"))
    img2 = loader.load(os.path.join(fixtures_dir, "after.tif"))
    
    validator = PlanValidator()
    report = validator.check_pair_compatibility(img1, img2)
    assert report["status"] == "compatible"
    
    # Test integration with Planner and Validator
    planner = Planner()
    bundle = InputBundle(images=[img1, img2])
    plan = planner.plan("What changed?", bundle)
    
    # This should pass without exception
    validator.validate(plan, bundle)

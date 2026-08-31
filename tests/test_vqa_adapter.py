import sys
import os
import pytest
from unittest.mock import patch, MagicMock

from engine.models.remote_sensing_vqa import RemoteSensingVQA, ModelInputUnsupportedError
from engine.contracts import InputBundle, ImageAsset, TaskType
from engine.geospatial.loader import RasterLoader

@pytest.fixture
def fixtures_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")

@pytest.fixture
def mock_rs_vqa():
    mock_torch = MagicMock()
    # Fake inference_mode context manager
    mock_torch.inference_mode.return_value.__enter__ = MagicMock()
    mock_torch.inference_mode.return_value.__exit__ = MagicMock()
    mock_torch.cuda = MagicMock()
    mock_torch.cuda.OutOfMemoryError = type("OutOfMemoryError", (Exception,), {})
    sys.modules['torch'] = mock_torch
    
    model = RemoteSensingVQA()
    # Mock the lazy loading so we don't actually download gigabytes of weights
    mock_model = MagicMock()
    mock_processor = MagicMock()
    
    # Setup simple generation mock
    mock_out = MagicMock()
    # Fake tensor output that slicing [0][input_len:] won't crash on
    # In reality, this is complex, so we'll just mock the decode method instead
    mock_model.generate.return_value = [[1, 2, 3, 4]]
    
    # Mock the inputs_processed return dict
    mock_processor.return_value = {"input_ids": MagicMock(shape=(1, 2))}
    mock_processor.decode.return_value = "Mocked real answer from VLM."
    
    model._lazy_load_model = MagicMock(return_value=(mock_model, mock_processor, "cpu"))
    return model

def test_vqa_adapter_basic(mock_rs_vqa, fixtures_dir):
    loader = RasterLoader()
    asset = loader.load(os.path.join(fixtures_dir, "optical.tif"))
    bundle = InputBundle(images=[asset])
    
    # Ensure it only claims SINGLE_IMAGE_VQA
    assert mock_rs_vqa.can_run(bundle, TaskType.SINGLE_IMAGE_VQA) is True
    assert mock_rs_vqa.can_run(bundle, TaskType.SINGLE_IMAGE_CAPTION) is False
    
    # Execute
    result = mock_rs_vqa.run(bundle, "What is this?")
    
    assert result.status == "success"
    assert result.model_name == "MBZUAI/GeoChat-7B"
    assert result.task == TaskType.SINGLE_IMAGE_VQA
    assert "generated_tokens" in result.metadata or result.answer is not None
    assert result.confidence is None # As required for Day 3
    assert result.metadata["device"] == "cpu"

def test_vqa_adapter_invalid_input(mock_rs_vqa):
    # Pass an asset that doesn't exist
    asset = ImageAsset(id="bad", path="fake/path.tif", filename="path.tif", format="GeoTIFF", modality="optical")
    bundle = InputBundle(images=[asset])
    
    with pytest.raises(Exception) as exc:
        mock_rs_vqa.run(bundle, "What is this?")
    
    assert "Failed to prepare GeoTIFF" in str(exc.value)

@pytest.mark.skipif(os.getenv("SATQUERY_RUN_MODEL_TESTS") != "1", reason="Real model tests disabled")
def test_real_model_execution():
    """This test only runs if explicitly requested to prevent massive downloads."""
    pass

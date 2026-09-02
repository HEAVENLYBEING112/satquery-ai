import os
import sys
import pytest
import json
from unittest.mock import patch, MagicMock

from engine.models.remote_sensing_vqa import RemoteSensingVQA, ModelInputUnsupportedError
from engine.contracts import InputBundle, ImageAsset, TaskType
from engine.geospatial.loader import RasterLoader
import urllib.error

@pytest.fixture
def fixtures_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")

@pytest.fixture
def mock_rs_vqa():
    os.environ["SATQUERY_GEOCHAT_URL"] = "http://fake-url"
    model = RemoteSensingVQA()
    return model

@patch("urllib.request.urlopen")
def test_vqa_adapter_basic(mock_urlopen, mock_rs_vqa, fixtures_dir):
    loader = RasterLoader()
    asset = loader.load(os.path.join(fixtures_dir, "optical.tif"))
    bundle = InputBundle(images=[asset])

    assert mock_rs_vqa.can_run(bundle, TaskType.SINGLE_IMAGE_VQA) is True
    assert mock_rs_vqa.can_run(bundle, TaskType.SINGLE_IMAGE_CAPTION) is False

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({
        "status": "success",
        "task": "vqa",
        "raw_text": "Mocked real answer from VLM.",
        "metadata": {"model": "MBZUAI/GeoChat-7B"}
    }).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    result = mock_rs_vqa.run(bundle, "What is this?")

    assert result.status == "success"
    assert result.model_name == "MBZUAI/GeoChat-7B"
    assert result.task == TaskType.SINGLE_IMAGE_VQA
    assert result.answer == "Mocked real answer from VLM."
    assert result.confidence is None
    assert result.metadata.get("remote_url") == "http://fake-url"

def test_vqa_adapter_invalid_input(mock_rs_vqa):
    asset = ImageAsset(id="bad", path="fake/path.tif", filename="path.tif", format="GeoTIFF", modality="optical")
    bundle = InputBundle(images=[asset])

    with pytest.raises(Exception) as exc:
        mock_rs_vqa.run(bundle, "What is this?")

    assert "Failed to prepare" in str(exc.value)

@pytest.mark.skipif(os.getenv("SATQUERY_RUN_MODEL_TESTS") != "1", reason="Real model tests disabled")
def test_real_model_execution():
    pass

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import urllib.error
import json
from engine.contracts import InputBundle, ImageAsset, TaskType, EvidenceBundle
from engine.models.remote_sensing_vqa import RemoteSensingVQA
from engine.models.remote_sensing_grounding import RemoteSensingGrounding

# FastAPI test client
from fastapi.testclient import TestClient

@pytest.fixture
def mock_image_asset(tmp_path):
    from PIL import Image
    path = tmp_path / "test.jpg"
    img = Image.new('RGB', (1001, 1001), color='red')
    img.save(path)
    return ImageAsset(id="1", path=str(path), filename="test.jpg", format="JPEG", modality="optical")

def test_grounding_parser():
    model = RemoteSensingGrounding()

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("{<10><20><30><40>|<90>}", 504, 504, evidence)
    assert len(boxes) == 1
    assert boxes[0].coordinates == pytest.approx([50.4, 100.8, 151.2, 201.6])
    assert evidence.metadata["angles"][0] == 90

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("{<0><0><100><100>|<0>}", 1001, 1001, evidence)
    assert len(boxes) == 1
    assert boxes[0].coordinates == pytest.approx([0.0, 0.0, 1001.0, 1001.0])

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("{<50><50><100><100>|<45>}", 1200, 800, evidence)
    assert len(boxes) == 1
    assert boxes[0].coordinates == pytest.approx([600.0, 400.0, 1200.0, 800.0])

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("{<10><10><20><20>|<0>}{<30><30><40><40>|<1>}", 100, 100, evidence)
    assert len(boxes) == 2
    assert evidence.metadata["angles"] == [0, 1]

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("Some text {<10><20><30><40>|<90>} and {<5><5><10><10>|bad} </s>", 504, 504, evidence)
    assert len(boxes) == 1

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("{<110><20><30><40>|<90>}", 504, 504, evidence)
    assert len(boxes) == 0

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("{<10><20><30><40>}", 504, 504, evidence)
    assert len(boxes) == 0

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("{<10><20><30><40>|<90>}</s>", 504, 504, evidence)
    assert len(boxes) == 1

    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("{<40><50><10><20>|<90>}", 504, 504, evidence)
    assert len(boxes) == 1
    assert boxes[0].coordinates == pytest.approx([50.4, 100.8, 201.6, 252.0])

@patch("urllib.request.urlopen")
def test_vqa_remote_client_success(mock_urlopen, mock_image_asset):
    os.environ["SATQUERY_GEOCHAT_URL"] = "http://fake-worker:8000"

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({
        "status": "success",
        "task": "vqa",
        "raw_text": "A remote sensing image.",
        "metadata": {"model": "MBZUAI/GeoChat-7B"}
    }).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    model = RemoteSensingVQA()
    bundle = InputBundle(images=[mock_image_asset])

    res = model.run(bundle, "What is this?")
    assert res.status == "success"
    assert res.answer == "A remote sensing image."
    assert res.confidence is None

@patch("urllib.request.urlopen")
def test_grounding_remote_client_success(mock_urlopen, mock_image_asset):
    os.environ["SATQUERY_GEOCHAT_URL"] = "http://fake-worker:8000"

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({
        "status": "success",
        "task": "grounding",
        "raw_text": "Found it. {<0><0><100><100>|<0>}",
        "metadata": {"model": "MBZUAI/GeoChat-7B"}
    }).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    model = RemoteSensingGrounding()
    bundle = InputBundle(images=[mock_image_asset])

    res = model.run(bundle, "Find things")
    assert res.status == "success"
    assert len(res.evidence.bounding_boxes) == 1
    assert res.confidence is None

@patch("urllib.request.urlopen")
def test_remote_client_timeout(mock_urlopen, mock_image_asset):
    os.environ["SATQUERY_GEOCHAT_URL"] = "http://fake-worker:8000"
    os.environ["SATQUERY_GEOCHAT_TIMEOUT_SECONDS"] = "1.0"
    mock_urlopen.side_effect = urllib.error.URLError(TimeoutError("Timeout"))

    model = RemoteSensingVQA()
    bundle = InputBundle(images=[mock_image_asset])

    res = model.run(bundle, "What is this?")
    assert res.status == "success"
    assert res.evidence.metadata.get("fallback_triggered") is True
    assert "timeout" in res.evidence.metadata.get("fallback_reason", "").lower()

@patch("urllib.request.urlopen")
def test_remote_client_connection_error(mock_urlopen, mock_image_asset):
    os.environ["SATQUERY_GEOCHAT_URL"] = "http://fake-worker:8000"
    mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

    model = RemoteSensingVQA()
    bundle = InputBundle(images=[mock_image_asset])

    res = model.run(bundle, "What is this?")
    assert res.status == "success"
    assert res.evidence.metadata.get("fallback_triggered") is True

@patch("urllib.request.urlopen")
def test_remote_client_malformed_json(mock_urlopen, mock_image_asset):
    os.environ["SATQUERY_GEOCHAT_URL"] = "http://fake-worker:8000"

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b"Not JSON at all"
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    model = RemoteSensingVQA()
    bundle = InputBundle(images=[mock_image_asset])

    res = model.run(bundle, "What is this?")
    assert res.status == "success"
    assert res.evidence.metadata.get("fallback_triggered") is True
    assert "Malformed JSON" in res.evidence.metadata.get("fallback_reason", "")

@patch("urllib.request.urlopen")
def test_remote_client_missing_raw_text(mock_urlopen, mock_image_asset):
    os.environ["SATQUERY_GEOCHAT_URL"] = "http://fake-worker:8000"

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({"status": "success"}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    model = RemoteSensingVQA()
    bundle = InputBundle(images=[mock_image_asset])

    res = model.run(bundle, "What is this?")
    assert res.status == "success"
    assert res.evidence.metadata.get("fallback_triggered") is True
    assert "missing" in res.evidence.metadata.get("fallback_reason", "")

@patch("urllib.request.urlopen")
def test_remote_client_http_error(mock_urlopen, mock_image_asset):
    os.environ["SATQUERY_GEOCHAT_URL"] = "http://fake-worker:8000"

    mock_resp = MagicMock()
    mock_resp.status = 500
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    model = RemoteSensingVQA()
    bundle = InputBundle(images=[mock_image_asset])

    res = model.run(bundle, "What is this?")
    assert res.status == "success"
    assert res.evidence.metadata.get("fallback_triggered") is True
    assert "HTTP 500" in res.evidence.metadata.get("fallback_reason", "")

def test_remote_client_fallback_when_unset(mock_image_asset):
    if "SATQUERY_GEOCHAT_URL" in os.environ:
        del os.environ["SATQUERY_GEOCHAT_URL"]

    model = RemoteSensingVQA()
    bundle = InputBundle(images=[mock_image_asset])

    res = model.run(bundle, "What is this?")
    assert res.status == "success"
    assert res.evidence.metadata.get("fallback_triggered") is True

@pytest.mark.skipif(not os.getenv("SATQUERY_GEOCHAT_URL"), reason="Real remote worker not configured")
def test_real_remote_worker_integration(mock_image_asset):
    model = RemoteSensingVQA()
    bundle = InputBundle(images=[mock_image_asset])
    res = model.run(bundle, "Describe this image.")
    assert res.status == "success"

# FastAPI Worker Tests using mocked GeoChat internals
@pytest.fixture
def mock_geochat_worker():
    import sys
    sys.modules['geochat'] = MagicMock()
    sys.modules['geochat.model'] = MagicMock()
    sys.modules['geochat.model.builder'] = MagicMock()
    sys.modules['geochat.conversation'] = MagicMock()
    sys.modules['geochat.constants'] = MagicMock()
    sys.modules['geochat.mm_utils'] = MagicMock()
    sys.modules['torch'] = MagicMock()

    # Must reset globals so tests are isolated if needed, or just let them be mocked once
    import services.geochat_worker.main as worker_main
    worker_main.model = None

    from services.geochat_worker.main import app
    client = TestClient(app)
    return client

def test_worker_health(mock_geochat_worker):
    import services.geochat_worker.main as worker_main
    worker_main.model = None

    with patch('services.geochat_worker.main.load_geochat') as mock_load:
        response = mock_geochat_worker.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["model"] == "MBZUAI/GeoChat-7B"
        assert data["model_loaded"] is False
        mock_load.assert_not_called()

def test_worker_invalid_task(mock_geochat_worker):
    response = mock_geochat_worker.post("/generate", json={
        "task": "invalid",
        "query": "hello",
        "image_base64": "fake"
    })
    assert response.status_code == 400
    assert "task must be" in response.json()["detail"]

def test_worker_empty_query(mock_geochat_worker):
    response = mock_geochat_worker.post("/generate", json={
        "task": "vqa",
        "query": "   ",
        "image_base64": "fake"
    })
    assert response.status_code == 400
    assert "query must be non-empty" in response.json()["detail"]

def test_worker_malformed_base64(mock_geochat_worker):
    response = mock_geochat_worker.post("/generate", json={
        "task": "vqa",
        "query": "what is this",
        "image_base64": "not!base64!valid"
    })
    assert response.status_code == 400
    assert "malformed" in response.json()["detail"].lower() or "image" in response.json()["detail"].lower()

def test_worker_malformed_image(mock_geochat_worker):
    import base64
    bad_img = base64.b64encode(b"not an image").decode("utf-8")
    response = mock_geochat_worker.post("/generate", json={
        "task": "vqa",
        "query": "what is this",
        "image_base64": bad_img
    })
    assert response.status_code == 400
    assert "valid image" in response.json()["detail"]

def test_worker_vqa_success(mock_geochat_worker):
    import base64
    from PIL import Image
    import io
    img = Image.new('RGB', (100, 100), color='red')
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    with patch('services.geochat_worker.main.load_geochat') as mock_load:
        import services.geochat_worker.main as worker_main
        worker_main.model = MagicMock()
        worker_main.tokenizer = MagicMock()
        worker_main.image_processor = MagicMock()

        worker_main.model.generate.return_value = MagicMock()
        worker_main.tokenizer.batch_decode.return_value = ["Mock output"]

        response = mock_geochat_worker.post("/generate", json={
            "task": "vqa",
            "query": "What is this?",
            "image_base64": b64
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["task"] == "vqa"
        assert data["raw_text"] == "Mock output"

def test_worker_grounding_success(mock_geochat_worker):
    import base64
    from PIL import Image
    import io
    import sys

    img = Image.new('RGB', (100, 100), color='red')
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    with patch('services.geochat_worker.main.load_geochat') as mock_load:
        import services.geochat_worker.main as worker_main
        worker_main.model = MagicMock()
        worker_main.tokenizer = MagicMock()
        worker_main.image_processor = MagicMock()

        worker_main.model.generate.return_value = MagicMock()
        worker_main.tokenizer.batch_decode.return_value = ["{<10><20><30><40>|<90>}"]

        # We need to spy on the prompt being assembled.
        # It's assembled via geochat.conversation.conv_templates["llava_v1"].copy().append_message()
        mock_conv_instance = MagicMock()
        mock_conv_templates = sys.modules['geochat.conversation'].conv_templates
        mock_conv_templates.__getitem__.return_value.copy.return_value = mock_conv_instance
        sys.modules['geochat.constants'].DEFAULT_IMAGE_TOKEN = "<image>"

        # Test 1: Query without [grounding]
        response = mock_geochat_worker.post("/generate", json={
            "task": "grounding",
            "query": "Find the plane",
            "image_base64": b64
        })
        assert response.status_code == 200
        data = response.json()
        assert data["task"] == "grounding"
        assert data["raw_text"] == "{<10><20><30><40>|<90>}" # Raw text is unchanged

        # Verify [grounding] was added
        args, kwargs = mock_conv_instance.append_message.call_args_list[0]
        # args[1] is the qs string
        assert "[grounding]" in args[1]

        mock_conv_instance.reset_mock()

        # Test 2: Query already has [grounding]
        response = mock_geochat_worker.post("/generate", json={
            "task": "grounding",
            "query": "[grounding] Find the plane",
            "image_base64": b64
        })
        assert response.status_code == 200

        args, kwargs = mock_conv_instance.append_message.call_args_list[0]
        # Ensure it wasn't duplicated
        assert args[1].count("[grounding]") == 1

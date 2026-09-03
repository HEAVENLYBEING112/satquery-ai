import pytest
from fastapi.testclient import TestClient
import numpy as np
import io

from backend.main import app

client = TestClient(app)

def create_synthetic_tiff_bytes(shape, value=1000):
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.io import MemoryFile
    data = np.ones(shape, dtype=np.uint16) * value
    transform = from_origin(0, 0, 10, 10)
    with MemoryFile() as memfile:
        with memfile.open(
            driver='GTiff', height=shape[1], width=shape[2], count=shape[0],
            dtype=data.dtype, crs='+proj=latlong', transform=transform,
        ) as dst:
            dst.write(data)
        return memfile.read()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_analyze_vqa():
    tiff_bytes = create_synthetic_tiff_bytes((3, 10, 10))
    response = client.post(
        "/analyze",
        data={"query": "what is this?"},
        files=[("files", ("opt.tif", tiff_bytes, "image/tiff"))]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["task"] == "single_image_vqa"
    assert "answer" in data
    # Check that confidence remains None where unmeasured
    if "confidence" in data:
        assert data["confidence"] is None or isinstance(data["confidence"], float)

def test_analyze_grounding():
    tiff_bytes = create_synthetic_tiff_bytes((3, 10, 10))
    response = client.post(
        "/analyze",
        data={"query": "highlight buildings"},
        files=[("files", ("opt.tif", tiff_bytes, "image/tiff"))]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["task"] == "single_image_grounding"
    
    # Check bounding box serialization
    last_evidence = data["evidence"][-1]
    assert "bounding_boxes" in last_evidence
    assert isinstance(last_evidence["bounding_boxes"], list)

def test_analyze_temporal():
    t1_bytes = create_synthetic_tiff_bytes((3, 10, 10), value=1000)
    t2_bytes = create_synthetic_tiff_bytes((3, 10, 10), value=5000)
    
    response = client.post(
        "/analyze",
        data={"query": "what changed?"},
        files=[
            ("files", ("t1.tif", t1_bytes, "image/tiff")),
            ("files", ("t2.tif", t2_bytes, "image/tiff")),
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["task"] in ["temporal_change_detection", "temporal_change_description", "temporal_change_vqa"]
    
    # Check fallback/confidence is none
    assert data["confidence"] is None
    
    last_evidence = data["evidence"][-1]
    assert "change_statistics" in last_evidence

def test_analyze_optical_sar():
    opt_bytes = create_synthetic_tiff_bytes((3, 10, 10))
    sar_bytes = create_synthetic_tiff_bytes((2, 10, 10))
    
    response = client.post(
        "/analyze",
        data={"query": "fuse optical and sar"},
        files=[
            ("files", ("opt.tif", opt_bytes, "image/tiff")),
            ("files", ("sar.tif", sar_bytes, "image/tiff")),
        ]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["task"] == "cross_modal_optical_sar"
    
    # Fallback metadata serialization (only present if mode is real)
    import os
    if os.getenv("SATQUERY_MODEL_MODE") == "real":
        last_evidence = data["evidence"][-1]
        assert last_evidence["metadata"].get("fallback_triggered") == True

def test_analyze_invalid_request():
    # Test missing image
    response = client.post(
        "/analyze",
        data={"query": "what is this?"}
    )
    assert response.status_code == 422 # FastAPI missing file validation

def test_engine_validation_failure():
    # Provide 2 SAR images -> validation failure
    sar1_bytes = create_synthetic_tiff_bytes((2, 10, 10))
    sar2_bytes = create_synthetic_tiff_bytes((2, 10, 10))
    
    response = client.post(
        "/analyze",
        data={"query": "what changed?"}, # Will attempt temporal or fail planning
        files=[
            ("files", ("sar1.tif", sar1_bytes, "image/tiff")),
            ("files", ("sar2.tif", sar2_bytes, "image/tiff")),
        ]
    )
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "failed"
    assert len(data["errors"]) > 0

import os
import json
import pytest
from engine.data import RemoteSensingSample, ManifestDataset

@pytest.fixture
def fixtures_dir():
    return os.path.join(os.path.dirname(__file__), "fixtures")

@pytest.fixture
def sample_manifest(fixtures_dir):
    manifest_path = os.path.join(fixtures_dir, "test_manifest.json")
    data = [
        {"id": "s1", "images": ["fake1.tif"], "question": "Q1", "answer": "A1"},
        {"id": "s2", "images": ["fake2.tif"], "question": "Q2", "answer": "A2"}
    ]
    with open(manifest_path, "w") as f:
        json.dump(data, f)
    return manifest_path
    
def test_manifest_dataset(sample_manifest):
    dataset = ManifestDataset(sample_manifest, "test_ds")
    
    assert dataset.name == "test_ds"
    assert len(dataset) == 2
    
    sample = dataset.get_sample(0)
    assert sample.id == "s1"
    assert sample.question == "Q1"
    assert sample.answer == "A1"
    
def test_data_leakage(sample_manifest):
    dataset = ManifestDataset(sample_manifest)
    
    # In a real scenario we'd check train/val/test splits don't overlap IDs
    # For now just verifying we can read the IDs
    ids = set([s.id for s in dataset.iter_samples()])
    assert "s1" in ids
    assert "s2" in ids
    assert len(ids) == 2

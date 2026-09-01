import json
from typing import List
from .base import RemoteSensingDataset, RemoteSensingSample

class ManifestDataset(RemoteSensingDataset):
    """Loads datasets from a standard JSON manifest."""
    def __init__(self, manifest_path: str, dataset_name: str = "manifest"):
        self._name = dataset_name
        self.samples = []
        
        with open(manifest_path, 'r') as f:
            data = json.load(f)
            for item in data:
                self.samples.append(RemoteSensingSample(
                    id=item.get("id", ""),
                    images=item.get("images", []),
                    question=item.get("question"),
                    answer=item.get("answer"),
                    caption=item.get("caption"),
                    task=item.get("task", "unknown"),
                    source_dataset=self._name
                ))
                
    @property
    def name(self) -> str:
        return self._name
        
    def __len__(self) -> int:
        return len(self.samples)
        
    def get_sample(self, index: int) -> RemoteSensingSample:
        return self.samples[index]

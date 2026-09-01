from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class RemoteSensingSample:
    id: str
    images: List[str]  # file paths
    question: Optional[str] = None
    answer: Optional[str] = None
    caption: Optional[str] = None
    regions: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    task: str = "unknown"
    source_dataset: str = "unknown"

class RemoteSensingDataset(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def __len__(self) -> int:
        pass
        
    @abstractmethod
    def get_sample(self, index: int) -> RemoteSensingSample:
        pass
        
    def iter_samples(self):
        for i in range(len(self)):
            yield self.get_sample(i)

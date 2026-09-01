from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from engine.contracts import SpecialistResult, InputBundle, TaskType

class ModelLoadError(Exception):
    pass
    
class ModelInputUnsupportedError(Exception):
    pass

class SpecialistModel(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def supported_tasks(self) -> List[TaskType]:
        ...

    @abstractmethod
    def can_run(self, inputs: InputBundle, task: TaskType) -> bool:
        ...

    @abstractmethod
    def run(
        self,
        inputs: InputBundle,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> SpecialistResult:
        ...

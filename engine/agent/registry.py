from typing import Dict, List, Optional
from engine.models.base import SpecialistModel
from engine.contracts import TaskType, InputBundle
from engine.models.mocks import (
    MockVQA, MockCaptioner, MockGrounding,
    MockChangeDetector, MockChangeDescription,
    MockChangeVQA, MockOpticalSAR
)

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, SpecialistModel] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(MockVQA())
        self.register(MockCaptioner())
        self.register(MockGrounding())
        self.register(MockChangeDetector())
        self.register(MockChangeDescription())
        self.register(MockChangeVQA())
        self.register(MockOpticalSAR())

    def register(self, model: SpecialistModel):
        if model.name in self._models:
            raise ValueError(f"Model {model.name} is already registered.")
        self._models[model.name] = model

    def get(self, name: str) -> SpecialistModel:
        if name not in self._models:
            raise ValueError(f"Model {name} not found in registry.")
        return self._models[name]

    def list(self) -> List[str]:
        return list(self._models.keys())

    def find_compatible_specialist(self, task: TaskType, inputs: InputBundle) -> Optional[SpecialistModel]:
        for model in self._models.values():
            if model.can_run(inputs, task):
                return model
        return None

registry = ModelRegistry()

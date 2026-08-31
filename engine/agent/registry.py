from typing import Dict, Type
from engine.models.base import SpecialistModel
from engine.models.change import MockChangeDetector

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, SpecialistModel] = {}
        self._register_defaults()

    def _register_defaults(self):
        # Register mock models for initial development
        self.register("change_detector", MockChangeDetector())

    def register(self, name: str, model: SpecialistModel):
        self._models[name] = model

    def get_model(self, name: str) -> SpecialistModel:
        if name not in self._models:
            raise ValueError(f"Model {name} not found in registry.")
        return self._models[name]

    def find_model_for_task(self, task: str) -> SpecialistModel:
        for model in self._models.values():
            if task in model.supported_tasks:
                return model
        return None

registry = ModelRegistry()

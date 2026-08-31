import os
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
        # Mocks are always available
        self.register(MockVQA())
        self.register(MockCaptioner())
        self.register(MockGrounding())
        self.register(MockChangeDetector())
        self.register(MockChangeDescription())
        self.register(MockChangeVQA())
        self.register(MockOpticalSAR())
        
        # Real models registered based on configuration
        mode = os.getenv("SATQUERY_MODEL_MODE", "mock").lower()
        if mode == "real":
            from engine.models.remote_sensing_vqa import RemoteSensingVQA
            self.register(RemoteSensingVQA())

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
        mode = os.getenv("SATQUERY_MODEL_MODE", "mock").lower()
        
        # If real mode, prefer real models for the specific task if available
        if mode == "real" and task == TaskType.SINGLE_IMAGE_VQA:
            if "RemoteSensingVQA" in self._models:
                model = self._models["RemoteSensingVQA"]
                if model.can_run(inputs, task):
                    return model
                    
        # Fallback to general compatibility (which includes mocks)
        for model in self._models.values():
            if model.can_run(inputs, task):
                # Avoid returning the mock if we explicitly want real, though usually we just rely on planner/steps
                return model
                
        return None

registry = ModelRegistry()

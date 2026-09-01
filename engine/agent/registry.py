import os
from typing import Dict, List, Optional
from engine.models.base import SpecialistModel
from engine.contracts import TaskType, InputBundle
from engine.models.mocks import (
    MockVQA, MockCaptioner, MockGrounding, MockOpticalSAR
)

from engine.models.change_detection import BaselineChangeDetector
from engine.models.change_description import MockChangeDescription
from engine.models.change_vqa import MockChangeVQA
from engine.models.optical_sar import OpticalSARSpecialist
from engine.models.optical_sar_ai import OpticalSARAI

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, SpecialistModel] = {}
        # Register base deterministic models
        self.register(MockVQA())
        self.register(MockCaptioner())
        self.register(MockGrounding())
        self.register(BaselineChangeDetector())
        self.register(MockChangeDescription())
        self.register(MockChangeVQA())
        
        # Real models registered based on configuration
        mode = os.getenv("SATQUERY_MODEL_MODE", "mock").lower()
        if mode == "real":
            from engine.models.remote_sensing_vqa import RemoteSensingVQA
            from engine.models.remote_sensing_grounding import RemoteSensingGrounding
            self.register(RemoteSensingVQA())
            self.register(RemoteSensingGrounding())
            
            # AI Optical-SAR Registration with Graceful Fallback
            ai_model = OpticalSARAI()
            try:
                # Test lazy initialization safely if required by hardware
                import torch
                self.register(ai_model)
            except ImportError:
                print("PyTorch not found. Falling back to deterministic OpticalSARSpecialist.")
                fallback_model = OpticalSARSpecialist()
                # Alias the fallback model to the AI name so planner routes cleanly
                self._models["OpticalSARAI_DualEncoder"] = fallback_model
        else:
            self.register(OpticalSARSpecialist())

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
        if mode == "real":
            if task == TaskType.SINGLE_IMAGE_VQA and "remote_sensing_vqa" in self._models:
                model = self._models["remote_sensing_vqa"]
                if model.can_run(inputs, task):
                    return model
            if task == TaskType.SINGLE_IMAGE_GROUNDING and "remote_sensing_grounding" in self._models:
                model = self._models["remote_sensing_grounding"]
                if model.can_run(inputs, task):
                    return model
                    
        # Fallback to general compatibility (which includes mocks)
        for model in self._models.values():
            if model.can_run(inputs, task):
                # Avoid returning the mock if we explicitly want real, though usually we just rely on planner/steps
                return model
                
        return None

registry = ModelRegistry()

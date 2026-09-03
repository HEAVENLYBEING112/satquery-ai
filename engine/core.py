import uuid
from typing import Optional

from engine.contracts import InputBundle, EngineResult
from engine.agent.planner import Planner, PlannerError
from engine.agent.registry import ModelRegistry
from engine.agent.executor import WorkflowExecutor

class SatQueryEngine:
    """
    Unified entry point for the SatQuery AI engine.
    Encapsulates planning, validation, and execution logic.
    """
    def __init__(self, registry: Optional[ModelRegistry] = None):
        self.registry = registry or ModelRegistry()
        self.planner = Planner()
        self.executor = WorkflowExecutor(self.registry)
        
    def analyze(self, inputs: InputBundle, query: str) -> EngineResult:
        """
        Processes a natural language query against a bundle of images.
        """
        request_id = str(uuid.uuid4())
        
        try:
            # 1. Plan the workflow based on the query and inputs
            plan = self.planner.plan(query, inputs)
            
            # 2. Execute the workflow
            result = self.executor.execute(plan, query, inputs)
            
            # (Validator is inherently integrated in executor and planner logic currently)
            return result
            
        except PlannerError as e:
            return self.executor._create_error_result(
                request_id=request_id,
                query=query,
                task=None,
                code="PLANNING_FAILED",
                message=str(e)
            )
        except Exception as e:
            # Log the actual error, but return a safe generic message to avoid leaking paths or secrets
            import logging
            logging.error(f"Internal engine error: {str(e)}")
            return self.executor._create_error_result(
                request_id=request_id,
                query=query,
                task=None,
                code="INTERNAL_ENGINE_ERROR",
                message="An unexpected engine error occurred. Please verify your inputs or contact support."
            )

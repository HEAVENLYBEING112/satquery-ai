import time
import uuid
from typing import List, Dict, Any
from engine.contracts import (
    WorkflowPlan, InputBundle, SpecialistResult, 
    EngineResult, EngineError, EvidenceBundle
)
from engine.evidence.validator import PlanValidator, ValidationError
from engine.agent.registry import ModelRegistry

class WorkflowExecutor:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.validator = PlanValidator()

    def execute(self, plan: WorkflowPlan, query: str, inputs: InputBundle, request_id: str = None) -> EngineResult:
        request_id = request_id or str(uuid.uuid4())
        
        try:
            self.validator.validate(plan, inputs)
        except ValidationError as e:
            return self._create_error_result(
                request_id=request_id,
                query=query,
                task=plan.task,
                code="INVALID_WORKFLOW",
                message=str(e)
            )

        specialist_results = []
        execution_trace = []
        all_evidence = []
        final_answer = None
        final_confidence = 1.0

        for step_idx, step in enumerate(plan.steps):
            start_time = time.time()
            
            try:
                model = self.registry.get(step.tool)
            except ValueError:
                return self._create_error_result(
                    request_id=request_id,
                    query=query,
                    task=plan.task,
                    code="NO_COMPATIBLE_TOOL",
                    message=f"Tool {step.tool} not found in registry."
                )

            if not model.can_run(inputs, plan.task):
                return self._create_error_result(
                    request_id=request_id,
                    query=query,
                    task=plan.task,
                    code="UNSUPPORTED_TASK",
                    message=f"Tool {step.tool} cannot run task {plan.task.value} with given inputs."
                )

            try:
                # Merge prior evidence statistics into parameters for downstream models
                # This fulfills the requirement that CD outputs are available to VQA/Description
                run_params = dict(step.parameters)
                if all_evidence:
                    last_evidence = all_evidence[-1]
                    if last_evidence:
                        run_params["previous_evidence"] = last_evidence
                        if last_evidence.change_statistics:
                            run_params["change_statistics"] = last_evidence.change_statistics
                
                result = model.run(inputs, query, run_params)
            except Exception as e:
                return self._create_error_result(
                    request_id=request_id,
                    query=query,
                    task=plan.task,
                    code="MODEL_EXECUTION_FAILED",
                    message=str(e)
                )

            duration_ms = int((time.time() - start_time) * 1000)
            
            specialist_results.append(result)
            all_evidence.append(result.evidence)
            final_answer = result.answer
            
            if result.confidence is not None:
                final_confidence = min(final_confidence, result.confidence)

            execution_trace.append({
                "step": step_idx + 1,
                "tool": step.tool,
                "task": plan.task.value,
                "status": result.status,
                "parameters": step.parameters,
                "duration_ms": duration_ms,
                "result_summary": result.answer
            })

        if final_confidence == 1.0:
            if any(r.confidence is not None for r in specialist_results):
                # At least one returned 1.0
                pass
            else:
                final_confidence = None
        if not specialist_results and final_confidence == 1.0:
            final_confidence = None

        return EngineResult(
            request_id=request_id,
            status="success",
            query=query,
            task=plan.task,
            answer=final_answer,
            confidence=final_confidence,
            specialist_results=specialist_results,
            evidence=all_evidence,
            execution_trace=execution_trace
        )

    def _create_error_result(self, request_id: str, query: str, task: Any, code: str, message: str) -> EngineResult:
        return EngineResult(
            request_id=request_id,
            status="failed",
            query=query,
            task=task,
            answer=None,
            confidence=None,
            specialist_results=[],
            evidence=[],
            execution_trace=[],
            errors=[EngineError(code=code, message=message)]
        )

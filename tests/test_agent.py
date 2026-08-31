import pytest
from engine.contracts import (
    TaskType, InputType, ImageAsset, InputBundle,
    WorkflowPlan, WorkflowStep, Evidence
)
from engine.agent.planner import Planner, PlannerError
from engine.evidence.validator import PlanValidator, ValidationError
from engine.agent.registry import registry
from engine.agent.executor import WorkflowExecutor
from engine.models.mocks import MockVQA

@pytest.fixture
def opt_img():
    return ImageAsset(id="1", path="opt.tif", filename="opt.tif", format="tif", modality="optical")

@pytest.fixture
def opt_img2():
    return ImageAsset(id="2", path="opt2.tif", filename="opt2.tif", format="tif", modality="optical")

@pytest.fixture
def sar_img():
    return ImageAsset(id="3", path="sar.tif", filename="sar.tif", format="tif", modality="sar")

def test_task_taxonomy():
    assert TaskType.SINGLE_IMAGE_VQA == "single_image_vqa"

def test_input_taxonomy():
    assert InputType.SINGLE_OPTICAL == "single_optical"
    assert InputType.TEMPORAL_OPTICAL == "temporal_optical"
    assert InputType.OPTICAL_SAR_PAIR == "optical_sar_pair"

def test_planner_single_image(opt_img):
    planner = Planner()
    bundle = InputBundle(images=[opt_img])
    
    plan = planner.plan("What is visible?", bundle)
    assert plan.task == TaskType.SINGLE_IMAGE_VQA
    
    plan = planner.plan("Describe this scene.", bundle)
    assert plan.task == TaskType.SINGLE_IMAGE_CAPTION
    
    plan = planner.plan("Highlight the water.", bundle)
    assert plan.task == TaskType.SINGLE_IMAGE_GROUNDING

def test_planner_temporal(opt_img, opt_img2):
    planner = Planner()
    bundle = InputBundle(images=[opt_img, opt_img2])
    
    plan = planner.plan("What changed?", bundle)
    assert plan.task == TaskType.TEMPORAL_CHANGE_DESCRIPTION
    
    plan = planner.plan("Has built-up increased?", bundle)
    assert plan.task == TaskType.TEMPORAL_CHANGE_VQA
    assert len(plan.steps) == 2

def test_planner_optical_sar(opt_img, sar_img):
    planner = Planner()
    bundle = InputBundle(images=[opt_img, sar_img])
    
    plan = planner.plan("Use optical and SAR together.", bundle)
    assert plan.task == TaskType.OPTICAL_SAR_ANALYSIS

def test_registry():
    model = registry.get("MockVQA")
    assert model.name == "MockVQA"
    assert "MockVQA" in registry.list()

def test_plan_validation(opt_img, opt_img2, sar_img):
    validator = PlanValidator()
    
    # Valid
    plan = WorkflowPlan(
        task=TaskType.TEMPORAL_CHANGE_DETECTION,
        input_type=InputType.TEMPORAL_OPTICAL,
        input_ids=["1", "2"],
        steps=[WorkflowStep(tool="MockChangeDetector")]
    )
    assert validator.validate(plan, InputBundle(images=[opt_img, opt_img2]))
    
    # Invalid (temporal with 1 image)
    with pytest.raises(ValidationError):
        validator.validate(plan, InputBundle(images=[opt_img]))
        
    # Invalid (Optical SAR with 2 optical)
    plan_fusion = WorkflowPlan(
        task=TaskType.OPTICAL_SAR_ANALYSIS,
        input_type=InputType.OPTICAL_SAR_PAIR,
        input_ids=["1", "2"],
        steps=[WorkflowStep(tool="MockOpticalSAR")]
    )
    with pytest.raises(ValidationError):
        validator.validate(plan_fusion, InputBundle(images=[opt_img, opt_img2]))

def test_executor(opt_img, opt_img2):
    executor = WorkflowExecutor(registry)
    planner = Planner()
    
    # Multi-step workflow test
    bundle = InputBundle(images=[opt_img, opt_img2])
    plan = planner.plan("Has built-up increased?", bundle)
    
    result = executor.execute(plan, "Has built-up increased?", bundle)
    if result.status == "failed":
        print([e.message for e in result.errors])
    assert result.status == "success"
    assert len(result.execution_trace) == 2
    assert result.answer == "Built-up area increased."
    assert result.confidence == 0.87

def test_executor_invalid_tool(opt_img):
    executor = WorkflowExecutor(registry)
    plan = WorkflowPlan(
        task=TaskType.SINGLE_IMAGE_VQA,
        input_type=InputType.SINGLE_OPTICAL,
        input_ids=["1"],
        steps=[WorkflowStep(tool="NonExistentModel")]
    )
    result = executor.execute(plan, "test", InputBundle(images=[opt_img]))
    assert result.status == "failed"
    assert result.errors[0].code == "NO_COMPATIBLE_TOOL"

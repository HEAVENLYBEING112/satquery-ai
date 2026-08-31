import sys
import uuid
from typing import List, Dict, Any

from engine.contracts import InputBundle, ImageAsset
from engine.agent.planner import Planner, PlannerError
from engine.agent.registry import registry
from engine.agent.executor import WorkflowExecutor

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_result(result, title="SATQUERY AI ENGINE"):
    print("=" * 50)
    print(title)
    print("=" * 50)
    print()
    
    print("QUERY:")
    print(f"{result.query}\n")

    if result.status == "failed":
        print("STATUS:")
        print("FAILED\n")
        print("ERRORS:")
        for err in result.errors:
            print(f"- {err.code}: {err.message}")
        print("=" * 50)
        return

    print("PLANNED TASK:")
    print(f"{result.task.value}\n")

    print("WORKFLOW:")
    for trace in result.execution_trace:
        print(f"{trace['step']}. {trace['tool']}")
    print()

    print("EXECUTION:")
    for trace in result.execution_trace:
        print(f"✓ {trace['tool']}")
    print()

    print("ANSWER:")
    print(f"{result.answer}\n")

    print("CONFIDENCE:")
    print(f"{result.confidence}\n")

    print("STATUS:")
    print("COMPLETED")
    print("=" * 50)
    print()

def main():
    planner = Planner()
    executor = WorkflowExecutor(registry)

    # Mock Image Assets
    optical_img_1 = ImageAsset(id="opt1", path="opt1.tif", filename="opt1.tif", format="GeoTIFF", modality="optical")
    optical_img_2 = ImageAsset(id="opt2", path="opt2.tif", filename="opt2.tif", format="GeoTIFF", modality="optical")
    sar_img_1 = ImageAsset(id="sar1", path="sar1.tif", filename="sar1.tif", format="GeoTIFF", modality="sar")

    test_cases = [
        {
            "title": "1. Single-image VQA",
            "query": "What is visible in this image?",
            "inputs": InputBundle(images=[optical_img_1])
        },
        {
            "title": "2. Caption",
            "query": "Describe the land-cover.",
            "inputs": InputBundle(images=[optical_img_1])
        },
        {
            "title": "3. Grounding",
            "query": "Highlight the water.",
            "inputs": InputBundle(images=[optical_img_1])
        },
        {
            "title": "4. Temporal change",
            "query": "What changed between these two dates?",
            "inputs": InputBundle(images=[optical_img_1, optical_img_2])
        },
        {
            "title": "5. Temporal change VQA",
            "query": "Has the built-up area increased?",
            "inputs": InputBundle(images=[optical_img_1, optical_img_2])
        },
        {
            "title": "6. Optical-SAR analysis",
            "query": "Use optical and SAR together.",
            "inputs": InputBundle(images=[optical_img_1, sar_img_1])
        },
        {
            "title": "7. Invalid input (Temporal query with 1 image)",
            "query": "What changed?",
            "inputs": InputBundle(images=[optical_img_1])
        },
        {
            "title": "8. Invalid input (Optical-SAR with 2 optical)",
            "query": "Use SAR and optical.",
            "inputs": InputBundle(images=[optical_img_1, optical_img_2])
        }
    ]

    for tc in test_cases:
        try:
            plan = planner.plan(tc["query"], tc["inputs"])
            result = executor.execute(plan, tc["query"], tc["inputs"])
        except PlannerError as e:
            result = executor._create_error_result(
                request_id=str(uuid.uuid4()),
                query=tc["query"],
                task=None,
                code="PLANNING_FAILED",
                message=str(e)
            )
        print_result(result, title=tc["title"])

if __name__ == "__main__":
    main()

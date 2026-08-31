import sys
import uuid
import argparse
from typing import List, Dict, Any

from engine.contracts import InputBundle, ImageAsset
from engine.agent.planner import Planner, PlannerError
from engine.agent.registry import registry
from engine.agent.executor import WorkflowExecutor
from engine.geospatial.loader import RasterLoader

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

def get_demo_cases():
    optical_img_1 = ImageAsset(id="opt1", path="opt1.tif", filename="opt1.tif", format="GeoTIFF", modality="optical", width=256, height=256)
    optical_img_2 = ImageAsset(id="opt2", path="opt2.tif", filename="opt2.tif", format="GeoTIFF", modality="optical", width=256, height=256)
    sar_img_1 = ImageAsset(id="sar1", path="sar1.tif", filename="sar1.tif", format="GeoTIFF", modality="sar", width=256, height=256)
    
    return [
        {"title": "1. Single-image VQA", "query": "What is visible in this image?", "inputs": InputBundle(images=[optical_img_1])},
        {"title": "2. Caption", "query": "Describe the land-cover.", "inputs": InputBundle(images=[optical_img_1])},
        {"title": "3. Grounding", "query": "Highlight the water.", "inputs": InputBundle(images=[optical_img_1])},
        {"title": "4. Temporal change", "query": "What changed between these two dates?", "inputs": InputBundle(images=[optical_img_1, optical_img_2])},
        {"title": "5. Temporal change VQA", "query": "Has the built-up area increased?", "inputs": InputBundle(images=[optical_img_1, optical_img_2])},
        {"title": "6. Optical-SAR analysis", "query": "Use optical and SAR together.", "inputs": InputBundle(images=[optical_img_1, sar_img_1])},
        {"title": "7. Invalid input (Temporal query with 1 image)", "query": "What changed?", "inputs": InputBundle(images=[optical_img_1])},
        {"title": "8. Invalid input (Optical-SAR with 2 optical)", "query": "Use SAR and optical.", "inputs": InputBundle(images=[optical_img_1, optical_img_2])}
    ]

def run_cases(cases, current_registry=None):
    if current_registry is None:
        current_registry = registry
        
    planner = Planner()
    executor = WorkflowExecutor(current_registry)
    
    for tc in cases:
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
        print_result(result, title=tc.get("title", "SATQUERY AI ENGINE"))

def main():
    parser = argparse.ArgumentParser(description="SatQuery AI Engine CLI")
    parser.add_argument("--image", type=str, help="Path to single image")
    parser.add_argument("--before", type=str, help="Path to before image (temporal)")
    parser.add_argument("--after", type=str, help="Path to after image (temporal)")
    parser.add_argument("--optical", type=str, help="Path to optical image")
    parser.add_argument("--sar", type=str, help="Path to SAR image")
    parser.add_argument("--query", type=str, help="Natural language query")
    parser.add_argument("--demo", action="store_true", help="Run the Day 1 demo workflows")
    parser.add_argument("--model", type=str, choices=["mock", "real"], default="mock", help="Model mode (mock or real)")
    
    args = parser.parse_args()
    
    import os
    os.environ["SATQUERY_MODEL_MODE"] = args.model
    
    # Reload registry if mode changed since it was loaded globally
    from engine.agent.registry import ModelRegistry
    global registry
    registry = ModelRegistry()
    
    if args.demo or len(sys.argv) == 1:
        run_cases(get_demo_cases(), registry)
        return
        
    if not args.query:
        print("Error: --query is required when using file inputs.")
        sys.exit(1)
        
    loader = RasterLoader()
    images = []
    
    if args.image:
        images.append(loader.load(args.image))
    if args.before:
        images.append(loader.load(args.before))
    if args.after:
        images.append(loader.load(args.after))
    if args.optical:
        images.append(loader.load(args.optical, modality_override="optical"))
    if args.sar:
        images.append(loader.load(args.sar, modality_override="sar"))
        
    if not images:
        print("Error: No images provided.")
        sys.exit(1)
        
    bundle = InputBundle(images=images)
    run_cases([{"title": "CLI Execution", "query": args.query, "inputs": bundle}], registry)

if __name__ == "__main__":
    main()

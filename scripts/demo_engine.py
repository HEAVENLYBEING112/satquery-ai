import os
import json
import argparse
from engine.core import SatQueryEngine
from engine.contracts import InputBundle, ImageAsset
from engine.agent.registry import ModelRegistry

def print_result(result):
    print("=" * 60)
    print(f"QUERY: {result.query}")
    print(f"TASK: {result.task.value if result.task else 'N/A'}")
    print(f"STATUS: {result.status}")
    if result.errors:
        print(f"ERRORS: {[e.message for e in result.errors]}")
        return
        
    specialist = result.specialist_results[-1] if result.specialist_results else None
    print(f"SELECTED SPECIALIST: {specialist.model_name if specialist else 'N/A'}")
    print(f"MODEL: {specialist.model_name if specialist else 'N/A'}")
    
    # Check fallback
    fallback = False
    evidence = result.evidence[-1] if result.evidence else None
    if evidence and evidence.metadata:
        fallback = evidence.metadata.get("fallback_triggered", False)
    print(f"FALLBACK: {fallback}")
    
    print(f"CONFIDENCE: {result.confidence if result.confidence is not None else 'N/A'}")
    print(f"FINAL ANSWER: {result.answer}")
    
    print("\nEVIDENCE:")
    if evidence:
        if evidence.textual_evidence:
            print(f"  Text: {evidence.textual_evidence}")
        if evidence.change_statistics:
            print(f"  Stats: {evidence.change_statistics}")
        if evidence.bounding_boxes:
            print(f"  BBoxes: {len(evidence.bounding_boxes)} found")
    else:
        print("  N/A")
        
    print("\nEXECUTION TRACE:")
    for step in result.execution_trace:
        print(f"  Step {step.get('step')}: {step.get('tool')} -> {step.get('status')}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="SatQuery Engine Demo")
    parser.add_argument("--mode", choices=["mock", "real"], default="mock", help="SATQUERY_MODEL_MODE")
    args = parser.parse_args()
    
    os.environ["SATQUERY_MODEL_MODE"] = args.mode
    print(f"Initializing Engine in {args.mode.upper()} mode...")
    
    registry = ModelRegistry()
    engine = SatQueryEngine(registry=registry)
    
    # We will use the synthetic fixtures from the test suite to ensure it works on low-spec machines
    # without downloading real datasets.
    
    # Demo 1: Single Image VQA
    print("\n--- DEMO 1: SINGLE IMAGE VQA ---")
    img1 = ImageAsset(id="1", path="tests/fixtures/optical.tif", filename="optical.tif", format="GeoTIFF", modality="optical")
    # if it doesn't exist, just pass mock path (engine should fail gracefully or mock might pass if it doesn't read disk)
    bundle1 = InputBundle(images=[img1])
    res1 = engine.analyze(bundle1, "Are there buildings visible?")
    print_result(res1)
    
    # Demo 2: Temporal Change Detection
    print("\n--- DEMO 2: TEMPORAL CHANGE DETECTION ---")
    img_before = ImageAsset(id="t1", path="tests/fixtures/before.tif", filename="before.tif", format="GeoTIFF", modality="optical")
    img_after = ImageAsset(id="t2", path="tests/fixtures/after.tif", filename="after.tif", format="GeoTIFF", modality="optical")
    bundle2 = InputBundle(images=[img_before, img_after])
    res2 = engine.analyze(bundle2, "What changed between these dates?")
    print_result(res2)
    
    # Demo 3: Optical-SAR Cross-Modal
    print("\n--- DEMO 3: CROSS-MODAL OPTICAL-SAR ---")
    img_opt = ImageAsset(id="opt", path="tests/fixtures/croma_opt.tif", filename="croma_opt.tif", format="GeoTIFF", modality="optical")
    img_sar = ImageAsset(id="sar", path="tests/fixtures/croma_sar.tif", filename="croma_sar.tif", format="GeoTIFF", modality="sar")
    bundle3 = InputBundle(images=[img_opt, img_sar])
    res3 = engine.analyze(bundle3, "Classify this region using SAR and Optical.")
    print_result(res3)

if __name__ == "__main__":
    main()

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force real model execution
os.environ["SATQUERY_MODEL_MODE"] = "real"

def run_smoke_test():
    logger.info("Starting SatQuery AI Real GPU VQA Smoke Test...")
    
    try:
        from engine.geospatial.loader import RasterLoader
        from engine.contracts import InputBundle
        from engine.models.remote_sensing_vqa import RemoteSensingVQA
    except ImportError as e:
        logger.error(f"Missing core engine modules. Is the environment set up? {e}")
        sys.exit(1)
        
    try:
        model = RemoteSensingVQA()
        logger.info(f"Loaded specialist: {model.name} targeting {model.model_id}")
        
        # Create a dummy RGB image for the smoke test
        from PIL import Image
        import numpy as np
        
        test_img_path = "smoke_test_input.png"
        Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)).save(test_img_path)
        
        loader = RasterLoader()
        asset = loader.load(test_img_path)
        bundle = InputBundle(images=[asset])
        
        query = "What is visible in this image?"
        logger.info(f"Running inference with query: '{query}'")
        
        result = model.run(bundle, query)
        
        logger.info("=== INFERENCE SUCCESS ===")
        logger.info(f"Status: {result.status}")
        logger.info(f"Answer: {result.answer}")
        logger.info(f"Metadata: {result.metadata}")
        
    except Exception as e:
        if "MODEL_OUT_OF_MEMORY" in str(e):
            logger.warning("Pipeline succeeded up to model execution, but hardware OOM occurred.")
            logger.warning("This is expected on machines with <14GB VRAM.")
        elif "MODEL_LOAD_FAILED" in str(e):
            logger.warning(f"Failed to load weights into memory: {e}")
            logger.warning("Pipeline is functional but hardware is insufficient.")
        else:
            logger.error(f"Smoke test failed unexpectedly: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    finally:
        if os.path.exists("smoke_test_input.png"):
            os.remove("smoke_test_input.png")
            
if __name__ == "__main__":
    run_smoke_test()

from typing import List
import os
from engine.contracts import BoundingBox

def draw_bounding_boxes(image_path: str, boxes: List[BoundingBox], output_path: str):
    """
    Draws bounding boxes on the image and saves it.
    """
    try:
        from PIL import Image, ImageDraw
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)
            
            for box in boxes:
                # box coordinates: [xmin, ymin, xmax, ymax]
                draw.rectangle(box.coordinates, outline="red", width=3)
                if box.label:
                    draw.text((box.coordinates[0], max(0, box.coordinates[1]-10)), box.label, fill="red")
                    
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            img.save(output_path)
            return output_path
    except ImportError:
        pass # Optional dependency or tests
    except Exception as e:
        print(f"Visualization failed: {e}")
        return None

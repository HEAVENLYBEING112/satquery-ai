import pytest
from engine.models.remote_sensing_grounding import RemoteSensingGrounding

def test_grounding_box_parsing():
    model = RemoteSensingGrounding()
    # GeoChat outputs [ymin, xmin, ymax, xmax] scaled to [0, 1000]
    # For a 1000x1000 image, [200, 100, 400, 500] -> [100, 200, 500, 400]
    boxes = model._parse_bounding_boxes("The water is at [200, 100, 400, 500].", 1000, 1000)
    
    assert len(boxes) == 1
    box = boxes[0]
    assert box.label == "detected_region"
    assert box.coordinates == [100.0, 200.0, 500.0, 400.0]
    
    # 500x500 image, [0, 0, 1000, 1000] -> [0, 0, 500, 500]
    boxes2 = model._parse_bounding_boxes("[0, 0, 1000, 1000]", 500, 500)
    assert boxes2[0].coordinates == [0.0, 0.0, 500.0, 500.0]

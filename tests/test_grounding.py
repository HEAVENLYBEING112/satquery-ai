import pytest
from engine.models.remote_sensing_grounding import RemoteSensingGrounding
from engine.contracts import EvidenceBundle

def test_grounding_box_parsing():
    model = RemoteSensingGrounding()
    # GeoChat outputs {<x1><y1><x2><y2>|<angle>} scaled to 0-100
    evidence = EvidenceBundle()
    boxes = model._parse_bounding_boxes("The water is at {<20><10><40><50>|<90>}", 1000, 1000, evidence)

    assert len(boxes) == 1
    box = boxes[0]
    assert box.label == "detected_region"
    assert box.coordinates == pytest.approx([200.0, 100.0, 400.0, 500.0])

    # 500x500 image
    evidence2 = EvidenceBundle()
    boxes2 = model._parse_bounding_boxes("{<0><0><100><100>|<0>}", 500, 500, evidence2)
    assert len(boxes2) == 1
    assert boxes2[0].coordinates == pytest.approx([0.0, 0.0, 500.0, 500.0])

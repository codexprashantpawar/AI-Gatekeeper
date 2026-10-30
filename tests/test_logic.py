import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from app.evidence import crop, save_event
from app.types import Detection


def _center_inside(inner, outer):
    from app.pipeline import _center_inside as f
    return f(inner, outer)


def test_center_inside():
    assert _center_inside((10, 10, 20, 20), (0, 0, 100, 100))
    assert not _center_inside((200, 200, 220, 220), (0, 0, 100, 100))


def test_crop_bounds():
    img = np.zeros((100, 100, 3), np.uint8)
    assert crop(img, (-10, -10, 50, 50)).shape[0] > 0


def test_save_event(tmp_path):
    img = np.zeros((200, 200, 3), np.uint8)
    dets = [Detection("vehicle", "car", 0.9, (10, 10, 150, 150)),
            Detection("plate", "plate", 0.8, (50, 100, 100, 120), linked_vehicle=0)]
    meta, d = save_event(img, dets, "T", out_dir=tmp_path)
    assert (d / "original.jpg").exists() and (d / "event.json").exists()
    assert "plate_ocr" in meta

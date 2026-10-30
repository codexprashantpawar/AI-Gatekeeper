"""Phase 1: verify dependencies, models, classes, camera."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings


def step(name, fn):
    try:
        print(f"[ OK ] {name}: {fn()}")
    except Exception as e:
        print(f"[FAIL] {name}: {type(e).__name__}: {e}")


def libs():
    import cv2, torch, transformers, ultralytics
    return (f"cv2 {cv2.__version__}, torch {torch.__version__} "
            f"(cuda={torch.cuda.is_available()}), transformers {transformers.__version__}, "
            f"ultralytics {ultralytics.__version__}")


def objects():
    from app.detectors.hf_objects import HFObjectDetector
    d = HFObjectDetector(settings.hf_object_model, settings.conf_objects)
    return f"{settings.hf_object_model} loaded, {len(d.classes())} classes"


def plate():
    from app.detectors.plate import PlateDetector
    return f"classes={PlateDetector(settings.plate_weights, settings.conf_plate).classes()}"


def cam():
    from app.camera import open_source, read_with_retry
    f = read_with_retry(open_source(settings.camera_url))
    return f"frame {f.shape[1]}x{f.shape[0]}"


if __name__ == "__main__":
    step("libraries", libs)
    step("object model (vehicle/animal)", objects)
    step("plate model", plate)
    step("camera", cam)

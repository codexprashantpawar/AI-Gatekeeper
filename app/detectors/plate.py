"""Number-plate DETECTION only (no OCR). Uses the pretrained HF plate
detector weights (best.pt) you cloned."""
from pathlib import Path

from app.config import settings
from app.config import settings
from app.types import Detection


class PlateDetector:
    def __init__(self, weights: str, conf: float):
        from ultralytics import YOLO  # imported lazily
        if not weights or not Path(weights).is_file():
            raise FileNotFoundError(f"Plate weights not found: {weights!r}")
        self.model = YOLO(weights)
        self.conf = conf

    def classes(self):
        return dict(self.model.names)

    def detect(self, frame_bgr):
        out = []
        for b in self.model(frame_bgr, conf=self.conf, imgsz=settings.plate_imgsz,
                            verbose=False)[0].boxes:
            out.append(Detection("plate", self.model.names[int(b.cls[0])],
                                 float(b.conf[0]),
                                 tuple(float(v) for v in b.xyxy[0].tolist())))
        return out


class PlateReader:
    # its confidence stays ~0.99 even on wrong reads, so no confidence gate here
    def __init__(self, model):
        from fast_plate_ocr import LicensePlateRecognizer
        self.m = LicensePlateRecognizer(model)

    def read(self, img):
        return self.m.run(img)[0].plate if img.size else ""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    camera_url: str = os.getenv("CAMERA_URL", "http://192.0.0.2:8080")
    camera_id: str = os.getenv("CAMERA_ID", "PHONE-01")
    hf_object_model: str = os.getenv("HF_OBJECT_MODEL", "PekingU/rtdetr_r50vd")
    plate_weights: str = os.getenv("PLATE_WEIGHTS", "")
    conf_objects: float = float(os.getenv("CONF_OBJECTS", "0.5"))
    conf_plate: float = float(os.getenv("CONF_PLATE", "0.4"))
    plate_imgsz: int = int(os.getenv("PLATE_IMGSZ", "960"))
    ocr_model: str = os.getenv("OCR_MODEL", "cct-s-v2-global-model")
    cooldown_seconds: float = float(os.getenv("COOLDOWN_SECONDS", "10"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "output"))
    tz_offset_hours: float = float(os.getenv("LOCAL_TZ_OFFSET_HOURS", "5.5"))


settings = Settings()

# COCO class names the HF object model emits
VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck", "bicycle"}
ANIMAL_CLASSES = {"bird", "cat", "dog", "horse", "sheep", "cow",
                                    "elephant", "bear", "zebra", "giraffe"}
PERSON_CLASSES = {"person"}

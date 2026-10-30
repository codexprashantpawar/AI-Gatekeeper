"""Vehicle + animal detection with a Hugging Face pretrained model
(default: PekingU/rtdetr_r50vd, COCO classes, Apache-2.0)."""
import cv2
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForObjectDetection

from app.config import ANIMAL_CLASSES, PERSON_CLASSES, VEHICLE_CLASSES
from app.types import Detection


class HFObjectDetector:
    def __init__(self, model_id: str, conf: float):
        self.conf = conf
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModelForObjectDetection.from_pretrained(model_id)
        self.model.to(self.device).eval()
        self.id2label = self.model.config.id2label

    def classes(self):
        return sorted(set(self.id2label.values()))

    @torch.inference_mode()
    def detect(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        inputs = self.processor(images=img, return_tensors="pt").to(self.device)
        outputs = self.model(**inputs)
        res = self.processor.post_process_object_detection(
            outputs, threshold=self.conf,
            target_sizes=torch.tensor([img.size[::-1]]).to(self.device))[0]
        dets = []
        for score, label, box in zip(res["scores"], res["labels"], res["boxes"]):
            name = self.id2label[int(label)]
            if name in VEHICLE_CLASSES:
                kind = "vehicle"
            elif name in ANIMAL_CLASSES:
                kind = "animal"
            elif name in PERSON_CLASSES:
                kind = "person"
            else:
                continue
            dets.append(Detection(kind, name, float(score),
                                  tuple(float(v) for v in box.tolist())))
        return dets

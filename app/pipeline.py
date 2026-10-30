import time

from app.config import settings
from app.detectors.hf_objects import HFObjectDetector
from app.detectors.plate import PlateDetector
from app.evidence import save_event


def _center_inside(inner, outer):
    cx = (inner[0] + inner[2]) / 2
    cy = (inner[1] + inner[3]) / 2
    return outer[0] <= cx <= outer[2] and outer[1] <= cy <= outer[3]


class Pipeline:
    def __init__(self):
        self.objects = HFObjectDetector(settings.hf_object_model, settings.conf_objects)
        self.plates = PlateDetector(settings.plate_weights, settings.conf_plate)
        self._last_event = {}   # kind -> monotonic time (simple cooldown)

    def analyse(self, frame):
        dets = self.objects.detect(frame)
        plates = self.plates.detect(frame)
        vehicles = [i for i, d in enumerate(dets) if d.kind == "vehicle"]
        for p in plates:
            # Link plate to a vehicle only if its centre lies inside the vehicle box
            for vi in vehicles:
                if _center_inside(p.bbox, dets[vi].bbox):
                    p.linked_vehicle = vi
                    break
            dets.append(p)
        return dets

    def process(self, frame, camera_id=None, use_cooldown=True):
        dets = self.analyse(frame)
        if not dets:
            return None
        now = time.monotonic()
        if use_cooldown:
            kinds = {d.kind for d in dets}
            fresh = {k for k in kinds
                     if now - self._last_event.get(k, -1e9) >= settings.cooldown_seconds}
            if not fresh:
                return {"suppressed": True}
            for k in fresh:
                self._last_event[k] = now
        meta, folder = save_event(frame, dets, camera_id or settings.camera_id)
        meta["folder"] = str(folder)
        return meta

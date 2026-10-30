"""Save original frame, annotated frame, crops and event.json."""
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cv2

from app.config import settings


def crop(img, bbox, pad=0.05):
    h, w = img.shape[:2]
    x1, y1, x2, y2 = map(int, bbox)
    px, py = int((x2 - x1) * pad), int((y2 - y1) * pad)
    return img[max(0, y1 - py):min(h, y2 + py), max(0, x1 - px):min(w, x2 + px)]


def new_event_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:6]


def save_event(frame, dets, camera_id, out_dir=None):
    out_dir = Path(out_dir or settings.output_dir)
    event_id = new_event_id()
    d = out_dir / event_id
    d.mkdir(parents=True, exist_ok=True)

    now_utc = datetime.now(timezone.utc)
    local = now_utc + timedelta(hours=settings.tz_offset_hours)

    cv2.imwrite(str(d / "original.jpg"), frame)
    ann = frame.copy()
    records = []
    for i, det in enumerate(dets):
        x1, y1, x2, y2 = map(int, det.bbox)
        colour = {"vehicle": (255, 160, 0), "animal": (0, 200, 0),
                                    "plate": (0, 0, 255), "person": (0, 255, 255)}[det.kind]
        cv2.rectangle(ann, (x1, y1), (x2, y2), colour, 2)
        cv2.putText(ann, f"{det.extra.get('text') or det.kind + ':' + det.label} {det.confidence:.2f}",
                    (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colour, 2)
        fname = f"{det.kind}_{i}_{det.label.replace(' ', '_')}.jpg"
        cv2.imwrite(str(d / fname), crop(frame, det.bbox))
        records.append({
            "index": i, "kind": det.kind, "class": det.label,
            "confidence": round(det.confidence, 4),
            "bbox_xyxy": [round(v, 1) for v in det.bbox],
            "linked_vehicle_index": det.linked_vehicle,
            "plate_text": det.extra.get("text"),
            "crop_file": fname,
        })
    cv2.imwrite(str(d / "annotated.jpg"), ann)

    meta = {
        "event_id": event_id, "camera_id": camera_id,
        "timestamp_utc": now_utc.isoformat(),
        "local_time": local.strftime("%Y-%m-%d %H:%M:%S"),
        "original_file": "original.jpg", "annotated_file": "annotated.jpg",
        "plate_ocr": "fast-plate-ocr, best effort",
        "detections": records,
    }
    (d / "event.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta, d

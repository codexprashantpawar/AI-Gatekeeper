"""Phase 2: live test from phone camera (or RTSP/video file)."""
import argparse, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.camera import CameraError, open_source
from app.config import settings
from app.pipeline import Pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=settings.camera_url)
    ap.add_argument("--frames", type=int, default=30)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--no-cooldown", action="store_true")
    a = ap.parse_args()

    pipe = Pipeline()
    src = open_source(a.url)
    for i in range(a.frames):
        try:
            frame = src.read()
        except CameraError as e:
            print(f"[{i}] camera error: {e}")
            time.sleep(a.interval)
            continue
        res = pipe.process(frame, use_cooldown=not a.no_cooldown)
        if res is None:
            print(f"[{i}] nothing detected")
        elif res.get("suppressed"):
            print(f"[{i}] detected but within cooldown")
        else:
            print(f"[{i}] EVENT {res['event_id']} -> {res['folder']}")
            for d in res["detections"]:
                print(f"      {d['kind']:7} {d['class']:12} conf={d['confidence']}")
        time.sleep(a.interval)
    src.close()


if __name__ == "__main__":
    main()

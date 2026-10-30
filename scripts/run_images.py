"""Phase 2: run on a folder of test images."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2
from app.pipeline import Pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    a = ap.parse_args()
    pipe = Pipeline()
    for p in sorted(Path(a.folder).glob("*")):
        if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp"}:
            continue
        img = cv2.imread(str(p))
        if img is None:
            print(f"{p.name}: unreadable")
            continue
        res = pipe.process(img, use_cooldown=False)
        if res is None:
            print(f"{p.name}: nothing detected")
        else:
            print(f"{p.name}: {res['event_id']} -> {res['folder']}")
            for d in res["detections"]:
                print(f"      {d['kind']:7} {d['class']:12} conf={d['confidence']}")


if __name__ == "__main__":
    main()

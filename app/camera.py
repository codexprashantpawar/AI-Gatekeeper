"""Frame sources: phone HTTP snapshot, RTSP/video file."""
import time
from pathlib import Path

import cv2
import numpy as np
import requests


class CameraError(RuntimeError):
    pass


class HttpSnapshotSource:
    """IP Webcam (Android): GET <base>/shot.jpg"""

    def __init__(self, base_url: str, timeout: float = 5.0):
        self.url = base_url.rstrip("/") + "/shot.jpg"
        self.timeout = timeout

    def read(self):
        try:
            r = requests.get(self.url, timeout=self.timeout)
            r.raise_for_status()
        except requests.RequestException as e:
            raise CameraError(f"snapshot failed: {e}") from e
        img = cv2.imdecode(np.frombuffer(r.content, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise CameraError("could not decode snapshot")
        return img

    def close(self):
        pass


class VideoSource:
    """RTSP URL or video file path."""

    def __init__(self, src):
        self.src = src
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            raise CameraError(f"cannot open {src}")

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            raise CameraError("end of stream or read failure")
        return frame

    def close(self):
        self.cap.release()


def open_source(url: str):
    if url.isdigit():
        return VideoSource(int(url))
    if url.rstrip("/").endswith("/video"):
        return VideoSource(url)
    if url.startswith(("rtsp://", "rtmp://")) or Path(url).suffix.lower() in {
            ".mp4", ".avi", ".mov", ".mkv"}:
        return VideoSource(url)
    return HttpSnapshotSource(url)


def read_with_retry(source, retries=3, delay=1.0):
    last = None
    for _ in range(retries):
        try:
            return source.read()
        except CameraError as e:
            last = e
            time.sleep(delay)
    raise last

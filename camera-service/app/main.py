"""FootPass camera service (Phase 2).

Captures ON the ZimaBoard from a USB (V4L2) camera and streams to the browser,
so the browser never needs camera permission. One background thread owns the
device; the MJPEG stream and single-frame capture both read the latest frame,
so live preview and capture never fight over the camera.

Orientation (flip/rotate) is applied at the source, so the returned frame IS
the correctly-oriented original (mounted-facing cameras are mirrored).
"""
from __future__ import annotations

import base64
import os
import threading
import time

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

VERSION = os.environ.get("FOOTPASS_VERSION", "0.1.0")
INDEX = int(os.environ.get("FOOTPASS_CAMERA_INDEX", "0"))
WIDTH = int(os.environ.get("FOOTPASS_CAMERA_WIDTH", "1280"))
HEIGHT = int(os.environ.get("FOOTPASS_CAMERA_HEIGHT", "720"))
FLIP = os.environ.get("FOOTPASS_CAMERA_FLIP", "").lower()   # "", "h", "v", "hv"
ROTATE = int(os.environ.get("FOOTPASS_CAMERA_ROTATE", "0"))  # 0/90/180/270

# Quality thresholds (heuristic; tuned by the golden-set later).
DARK, BRIGHT, BLUR = 40.0, 220.0, 60.0


def _orient(frame: np.ndarray, flip: str, rotate: int) -> np.ndarray:
    if "h" in flip:
        frame = cv2.flip(frame, 1)
    if "v" in flip:
        frame = cv2.flip(frame, 0)
    if rotate == 90:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotate == 180:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    elif rotate == 270:
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame


def _resolve(flip: str | None, rotate: int | None) -> tuple[str, int]:
    """Per-request orientation overrides the env default."""
    f = FLIP if flip is None else flip.lower()
    r = ROTATE if rotate is None else rotate
    return f, r


class Camera:
    def __init__(self) -> None:
        self._cap: cv2.VideoCapture | None = None
        self._frame: np.ndarray | None = None
        self._lock = threading.Lock()
        self._running = False
        self.available = False

    def start(self) -> None:
        cap = cv2.VideoCapture(INDEX, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap = cv2.VideoCapture(INDEX)  # fallback to default backend
        if not cap.isOpened():
            self.available = False
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self._cap = cap
        self._running = True
        self.available = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self) -> None:
        assert self._cap is not None
        while self._running:
            ok, frame = self._cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            with self._lock:
                self._frame = frame  # store RAW; orientation applied at read time
            time.sleep(0.01)

    def latest(self, flip: str = "", rotate: int = 0) -> np.ndarray | None:
        with self._lock:
            frame = None if self._frame is None else self._frame.copy()
        return None if frame is None else _orient(frame, flip, rotate)

    def jpeg(self, quality: int, flip: str, rotate: int) -> bytes | None:
        frame = self.latest(flip, rotate)
        if frame is None:
            return None
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        return buf.tobytes() if ok else None


def assess(frame: np.ndarray) -> dict:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = float(gray.mean())
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    reasons: list[str] = []
    if brightness < DARK:
        reasons.append("too dark")
    if brightness > BRIGHT:
        reasons.append("too bright")
    if sharpness < BLUR:
        reasons.append("looks blurry")
    return {
        "brightness": round(brightness, 1),
        "sharpness": round(sharpness, 1),
        "status": "pass" if not reasons else "retake",
        "reasons": reasons,
    }


camera = Camera()
app = FastAPI(title="FootPass Camera", version=VERSION, docs_url="/camera/docs")


@app.on_event("startup")
def _startup() -> None:
    try:
        camera.start()
    except Exception:  # noqa: BLE001 - service must stay up even with no camera
        camera.available = False


@app.get("/camera/health")
def health() -> dict:
    return {"status": "healthy", "service": "camera", "version": VERSION}


@app.get("/camera/status")
def status() -> dict:
    return {
        "available": camera.available,
        "status": "ready" if camera.available else "no_camera",
        "device_index": INDEX,
        "width": WIDTH,
        "height": HEIGHT,
        "orientation": {"flip": FLIP, "rotate": ROTATE},
    }


def _mjpeg(flip: str, rotate: int):
    boundary = b"--frame"
    while True:
        jpg = camera.jpeg(75, flip, rotate)
        if jpg is None:
            time.sleep(0.1)
            continue
        yield boundary + b"\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
        time.sleep(0.05)  # ~20 fps cap


@app.get("/camera/stream")
def stream(flip: str | None = None, rotate: int | None = None) -> StreamingResponse:
    if not camera.available:
        raise HTTPException(status_code=503, detail="No camera available.")
    f, r = _resolve(flip, rotate)
    return StreamingResponse(_mjpeg(f, r), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/camera/capture")
def capture(flip: str | None = None, rotate: int | None = None) -> dict:
    if not camera.available:
        raise HTTPException(status_code=503, detail="No camera available.")
    f, r = _resolve(flip, rotate)
    frame = camera.latest(f, r)
    if frame is None:
        raise HTTPException(status_code=503, detail="No frame yet — try again in a moment.")
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to encode frame.")
    h, w = frame.shape[:2]
    return {
        "ok": True,
        "width": int(w),
        "height": int(h),
        "device_index": INDEX,
        "quality": assess(frame),
        "image_b64": base64.b64encode(buf.tobytes()).decode("ascii"),
    }

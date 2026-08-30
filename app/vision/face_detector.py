from pathlib import Path

import cv2
import httpx
import numpy as np

MODEL_PATH = (
    Path(__file__).parent
    / "models"
    / "face_detection_yunet_2023mar.onnx"
)
MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
SCORE_THRESHOLD = 0.6
NMS_THRESHOLD = 0.3
TOP_K = 50


class FaceDetector:
    """Lightweight DNN face detector (YuNet), OpenCV's replacement for
    the legacy Haar Cascade API removed from cv2's Python bindings.

    The model weights are fetched on demand (like ultralytics' *.pt
    files) rather than committed to the repository."""

    def __init__(self):
        self._ensure_model()

        self.detector = cv2.FaceDetectorYN_create(
            str(MODEL_PATH),
            "",
            (0, 0),
            score_threshold=SCORE_THRESHOLD,
            nms_threshold=NMS_THRESHOLD,
            top_k=TOP_K
        )

    def _ensure_model(self) -> None:
        if MODEL_PATH.exists():
            return

        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

        with httpx.stream(
            "GET",
            MODEL_URL,
            follow_redirects=True,
            timeout=30.0
        ) as response:
            response.raise_for_status()

            tmp_path = MODEL_PATH.with_suffix(".onnx.tmp")
            with open(tmp_path, "wb") as file:
                file.writelines(response.iter_bytes())

            tmp_path.replace(MODEL_PATH)

    def detect_faces(self, image: np.ndarray) -> list[dict]:
        height, width = image.shape[:2]
        self.detector.setInputSize((width, height))

        _, detections = self.detector.detect(image)

        if detections is None:
            return []

        faces = []

        for detection in detections:
            x, y, w, h = detection[:4]
            confidence = float(detection[14])

            x1 = max(0, int(x))
            y1 = max(0, int(y))
            x2 = min(width, int(x + w))
            y2 = min(height, int(y + h))

            faces.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": round(confidence, 4)
            })

        return faces

import cv2
import numpy as np
from PIL import Image

from app.vision.presentation_model import PresentationModel

CONFIDENCE_THRESHOLD = 0.6
MARGIN_RATIO = 0.25


class PresentationSignalEstimator:
    """Estimates a perceived-presentation signal for one detected face.

    The output is a coarse, low-confidence visual signal (hairstyle,
    clothing, facial features as picked up by a general-purpose CLIP
    model), never a claim about the person's actual sex or gender.
    Below CONFIDENCE_THRESHOLD the face is bucketed as "undetermined".
    """

    def __init__(self):
        self.model = PresentationModel()

    def estimate(self, image: np.ndarray, bbox: list[int]) -> dict:
        face_crop = self._crop_with_margin(image, bbox)
        pil_image = Image.fromarray(
            cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        )

        prediction = self.model.predict(pil_image)

        category = (
            prediction["best_category"]
            if prediction["confidence"] >= CONFIDENCE_THRESHOLD
            else "undetermined"
        )

        return {
            "category": category,
            "confidence": prediction["confidence"],
            "scores": prediction["scores"]
        }

    def _crop_with_margin(
        self,
        image: np.ndarray,
        bbox: list[int]
    ) -> np.ndarray:
        height, width = image.shape[:2]
        x1, y1, x2, y2 = bbox

        margin_x = int((x2 - x1) * MARGIN_RATIO)
        margin_y = int((y2 - y1) * MARGIN_RATIO)

        x1 = max(0, x1 - margin_x)
        y1 = max(0, y1 - margin_y)
        x2 = min(width, x2 + margin_x)
        y2 = min(height, y2 + margin_y)

        crop = image[y1:y2, x1:x2]

        if crop.size == 0:
            return image

        return crop

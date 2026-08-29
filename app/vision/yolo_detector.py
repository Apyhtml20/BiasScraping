from ultralytics import YOLO
import numpy as np

class YOLODetector:
    def __init__(self):
        self.model = YOLO("yolo11n.pt")

    def detect_people(self, image: np.ndarray) -> dict:
        results = self.model(image, verbose=False)
        people = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])

                if result.names[class_id] != "person":
                    continue

                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                people.append({
                    "confidence": round(confidence, 4),
                    "bbox": [
                        round(x1, 2),
                        round(y1, 2),
                        round(x2, 2),
                        round(y2, 2)
                    ]
                })

        return {
            "people_count": len(people),
            "people": people
        }
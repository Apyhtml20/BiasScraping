import httpx
import cv2
import numpy as np

class ImagePreprocessor:
    async def download(self, url: str) -> np.ndarray | None:
        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"}
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

            image_array = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                return None

            return self.resize(image)

        except Exception:
            return None

    def resize(
        self,
        image: np.ndarray,
        max_width: int = 1280
    ) -> np.ndarray:
        height, width = image.shape[:2]

        if width <= max_width:
            return image

        ratio = max_width / width
        new_height = int(height * ratio)

        return cv2.resize(
            image,
            (max_width, new_height),
            interpolation=cv2.INTER_AREA
        )

    def normalize(self, image: np.ndarray) -> np.ndarray:
        return image.astype(np.float32) / 255.0

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )
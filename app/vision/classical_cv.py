import cv2
import numpy as np

class ClassicalCVAnalyzer:
    def analyze(self, image: np.ndarray) -> dict:
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        return {
            "brightness": self.calculate_brightness(grayscale),
            "contrast": self.calculate_contrast(grayscale),
            "sharpness": self.calculate_sharpness(grayscale),
            "edge_density": self.calculate_edge_density(grayscale),
            "contours": self.count_contours(grayscale),
            "width": image.shape[1],
            "height": image.shape[0]
        }

    def calculate_brightness(self, image: np.ndarray) -> float:
        return round(float(np.mean(image)), 2)

    def calculate_contrast(self, image: np.ndarray) -> float:
        return round(float(np.std(image)), 2)

    def calculate_sharpness(self, image: np.ndarray) -> float:
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        return round(float(laplacian.var()), 2)

    def calculate_edge_density(self, image: np.ndarray) -> float:
        edges = cv2.Canny(image, 100, 200)

        edge_pixels = np.count_nonzero(edges)
        total_pixels = edges.size

        return round(float(edge_pixels / total_pixels), 4)

    def count_contours(self, image: np.ndarray) -> int:
        edges = cv2.Canny(image, 100, 200)

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        return len(contours)
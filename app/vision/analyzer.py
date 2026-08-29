import asyncio

from app.models.article import Article
from app.vision.preprocessing import ImagePreprocessor
from app.vision.classical_cv import ClassicalCVAnalyzer
from app.vision.yolo_detector import YOLODetector
from app.vision.fusion import VisionFusion


class VisionAnalyzer:
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.classical_cv = ClassicalCVAnalyzer()
        self.yolo = YOLODetector()
        self.fusion = VisionFusion()

    async def analyze(self, article: Article) -> dict:
        image_results = []

        for article_image in article.images:
            image = await self.preprocessor.download(article_image.url)

            if image is None:
                continue

            classical_result = self.classical_cv.analyze(image)
            yolo_result = self.yolo.detect_people(image)

            result = self.fusion.fuse(
                classical_result,
                yolo_result
            )

            result["image_id"] = article_image.id
            result["image_url"] = article_image.url
            result["alt"] = article_image.alt

            image_results.append(result)

        return self._build_report(image_results)

    def _build_report(self, image_results: list[dict]) -> dict:
        if not image_results:
            return {
                "module": "computer_vision",
                "images_analyzed": 0,
                "images_with_people": 0,
                "people_detected": 0,
                "average_prominence": 0.0,
                "score": 0,
                "images": []
            }

        images_with_people = sum(
            1
            for image in image_results
            if image["people_count"] > 0
        )

        people_detected = sum(
            image["people_count"]
            for image in image_results
        )

        average_prominence = sum(
            image["people_prominence"]
            for image in image_results
        ) / len(image_results)

        average_quality = sum(
            image["image_quality"]
            for image in image_results
        ) / len(image_results)

        score = self._calculate_score(
            average_quality,
            images_with_people,
            len(image_results)
        )

        return {
            "module": "computer_vision",
            "images_analyzed": len(image_results),
            "images_with_people": images_with_people,
            "people_detected": people_detected,
            "average_prominence": round(
                average_prominence,
                4
            ),
            "score": score,
            "images": image_results
        }

    def _calculate_score(
        self,
        average_quality: float,
        images_with_people: int,
        total_images: int
    ) -> int:
        if total_images == 0:
            return 0

        representation_ratio = (
            images_with_people / total_images
        ) * 100

        score = (
            average_quality * 0.4
            + representation_ratio * 0.6
        )

        return max(0, min(100, round(score)))
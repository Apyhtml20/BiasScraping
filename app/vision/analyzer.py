
from app.scraping_system.article_extractor import Article
from app.vision.classical_cv import ClassicalCVAnalyzer
from app.vision.face_detector import FaceDetector
from app.vision.fusion import VisionFusion
from app.vision.preprocessing import ImagePreprocessor
from app.vision.presentation_signal import PresentationSignalEstimator
from app.vision.representation_aggregator import RepresentationAggregator
from app.vision.yolo_detector import YOLODetector

REPRESENTATION_DISCLAIMER = (
    "Ces categories refletent des signaux visuels de presentation percue "
    "(coiffure, vetements, traits estimes par un modele CLIP zero-shot) "
    "agreges au niveau de la page. Elles ne constituent en aucun cas une "
    "identification du sexe ou du genre reel des personnes photographiees."
)


class VisionAnalyzer:
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
        self.classical_cv = ClassicalCVAnalyzer()
        self.yolo = YOLODetector()
        self.fusion = VisionFusion()
        self.face_detector = FaceDetector()
        self.presentation_signal = PresentationSignalEstimator()
        self.representation_aggregator = RepresentationAggregator()

    async def analyze(self, article: Article) -> dict:
        image_results = []
        all_faces = []

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

            faces = self._analyze_faces(image)

            result["image_id"] = article_image.id
            result["image_url"] = article_image.url
            result["alt"] = article_image.alt
            result["faces"] = faces

            all_faces.extend(faces)

            image_results.append(result)

        return self._build_report(image_results, all_faces)

    def _analyze_faces(self, image) -> list[dict]:
        detections = self.face_detector.detect_faces(image)
        faces = []

        for detection in detections:
            signal = self.presentation_signal.estimate(
                image,
                detection["bbox"]
            )

            faces.append({
                "bbox": detection["bbox"],
                "category": signal["category"],
                "confidence": signal["confidence"],
                "scores": signal["scores"]
            })

        return faces

    def _build_report(
        self,
        image_results: list[dict],
        all_faces: list[dict]
    ) -> dict:
        if not image_results:
            return {
                "module": "computer_vision",
                "images_analyzed": 0,
                "images_with_people": 0,
                "people_detected": 0,
                "average_prominence": 0.0,
                "score": 0,
                "representation": {
                    **self.representation_aggregator.aggregate([]),
                    "images_with_faces": 0,
                    "disclaimer": REPRESENTATION_DISCLAIMER
                },
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

        images_with_faces = sum(
            1
            for image in image_results
            if image["faces"]
        )

        representation = {
            **self.representation_aggregator.aggregate(all_faces),
            "images_with_faces": images_with_faces,
            "disclaimer": REPRESENTATION_DISCLAIMER
        }

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
            "representation": representation,
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
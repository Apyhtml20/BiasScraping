import uuid

from app.scraping_system.article_extractor import Article
from app.reports.scoring import InclusivityScorer
from app.reports.recommendations import RecommendationEngine


class ReportManager:
    def __init__(self):
        self.scorer = InclusivityScorer()
        self.recommendation_engine = RecommendationEngine()

    def create_report(
        self,
        article: Article,
        nlp_report: dict,
        vision_report: dict
    ) -> dict:
        nlp_score = nlp_report.get("score", 0)
        vision_score = vision_report.get("score", 0)

        overall_score = self.scorer.calculate_overall_score(
            nlp_score,
            vision_score
        )

        recommendations = self.recommendation_engine.generate(
            nlp_report,
            vision_report
        )

        issues = self._collect_issues(
            nlp_report,
            vision_report
        )

        return {
            "audit_id": str(uuid.uuid4()),
            "url": article.url,
            "title": article.title,
            "inclusivity_score": overall_score,
            "summary": {
                "nlp_score": nlp_score,
                "vision_score": vision_score,
                "total_issues": len(issues)
            },
            "issues": issues,
            "recommendations": recommendations,
            "metadata": {
                "paragraphs_analyzed": len(
                    article.paragraphs
                ),
                "images_found": len(article.images),
                "images_analyzed": vision_report.get(
                    "images_analyzed",
                    0
                )
            }
        }

    def _collect_issues(
        self,
        nlp_report: dict,
        vision_report: dict
    ) -> list[dict]:
        issues = []

        for issue in nlp_report.get("issues", []):
            issues.append({
                "module": "nlp",
                **issue
            })

        images_analyzed = vision_report.get(
            "images_analyzed",
            0
        )

        images_with_people = vision_report.get(
            "images_with_people",
            0
        )

        if (
            images_analyzed > 0
            and images_with_people / images_analyzed < 0.3
        ):
            issues.append({
                "module": "computer_vision",
                "type": "low_visual_representation",
                "severity": "medium",
                "message": (
                    "Few article images contain visible people."
                )
            })

        return issues
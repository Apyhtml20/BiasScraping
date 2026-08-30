import uuid

from app.reports.recommendations import RecommendationEngine
from app.reports.scoring import InclusivityScorer
from app.scraping_system.article_extractor import Article


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
        representation = vision_report.get("representation", {})
        representation_score = representation.get("representation_score")

        overall_score = self.scorer.calculate_overall_score(
            nlp_score,
            vision_score,
            representation_score
        )

        score_breakdown = self.scorer.build_breakdown(
            nlp_score,
            vision_score,
            representation_score
        )

        score_explanation = self.scorer.explain_breakdown(
            score_breakdown
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
            "score_breakdown": score_breakdown,
            "score_explanation": score_explanation,
            "summary": {
                "nlp_score": nlp_score,
                "vision_score": vision_score,
                "representation_score": representation_score,
                "total_issues": len(issues)
            },
            "representation": representation,
            "issues": issues,
            "recommendations": recommendations,
            "images": vision_report.get("images", []),
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

        representation = vision_report.get("representation", {})
        representation_score = representation.get("representation_score")

        if (
            representation_score is not None
            and representation_score < 40
        ):
            issues.append({
                "module": "representation",
                "type": "low_representation_diversity",
                "severity": "medium",
                "message": (
                    "The perceived visual presentation of people shown "
                    "on this page lacks diversity or balance."
                )
            })

        return issues
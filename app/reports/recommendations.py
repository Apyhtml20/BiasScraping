class RecommendationEngine:
    def generate(
        self,
        nlp_report: dict,
        vision_report: dict
    ) -> list[dict]:
        recommendations = []

        recommendations.extend(
            self._nlp_recommendations(nlp_report)
        )

        recommendations.extend(
            self._vision_recommendations(vision_report)
        )

        recommendations.extend(
            self._representation_recommendations(vision_report)
        )

        return recommendations

    def _nlp_recommendations(
        self,
        nlp_report: dict
    ) -> list[dict]:
        recommendations = []
        seen_types = set()

        for issue in nlp_report.get("issues", []):
            issue_type = issue["type"]

            if issue_type in seen_types:
                continue

            seen_types.add(issue_type)

            recommendation = self._get_nlp_recommendation(
                issue_type
            )

            if recommendation:
                recommendations.append({
                    "module": "nlp",
                    "type": issue_type,
                    "message": recommendation
                })

        return recommendations

    def _vision_recommendations(
        self,
        vision_report: dict
    ) -> list[dict]:
        recommendations = []

        images_analyzed = vision_report.get(
            "images_analyzed",
            0
        )

        images_with_people = vision_report.get(
            "images_with_people",
            0
        )

        if images_analyzed > 0:
            representation_ratio = (
                images_with_people / images_analyzed
            )

            if representation_ratio < 0.3:
                recommendations.append({
                    "module": "computer_vision",
                    "type": "low_visual_representation",
                    "message": (
                        "Consider using more visuals that "
                        "represent people and diverse contexts."
                    )
                })

        return recommendations

    def _representation_recommendations(
        self,
        vision_report: dict
    ) -> list[dict]:
        representation = vision_report.get("representation", {})
        representation_score = representation.get("representation_score")

        if representation_score is None or representation_score >= 40:
            return []

        return [{
            "module": "representation",
            "type": "low_representation_diversity",
            "message": (
                "Diversify the perceived visual presentation of people "
                "shown in this page's images to improve balance."
            )
        }]

    def _get_nlp_recommendation(
        self,
        issue_type: str
    ) -> str | None:
        recommendations = {
            "gendered_language": (
                "Replace gendered expressions with "
                "neutral or inclusive alternatives."
            ),
            "gender_stereotype": (
                "Review the sentence and avoid linking "
                "roles or qualities to a specific gender."
            ),
            "exclusionary_language": (
                "Use more inclusive wording that does not "
                "exclude specific groups."
            ),
            "potential_bias": (
                "Review this passage for potentially biased "
                "or stereotypical language."
            )
        }

        return recommendations.get(issue_type)
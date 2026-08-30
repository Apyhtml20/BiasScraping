COMPONENT_WEIGHTS = {
    "nlp": 0.5,
    "vision": 0.25,
    "representation": 0.25
}

COMPONENT_LABELS = {
    "nlp": "l'analyse du texte (langage biaise ou exclusif)",
    "vision": (
        "l'analyse visuelle globale (qualite des images et presence "
        "de personnes)"
    ),
    "representation": (
        "la diversite et l'equilibre de representation visuelle percue"
    )
}


class InclusivityScorer:
    def calculate_overall_score(
        self,
        nlp_score: float,
        vision_score: float,
        representation_score: float | None = None
    ) -> int:
        breakdown = self.build_breakdown(
            nlp_score,
            vision_score,
            representation_score
        )

        total = sum(component["contribution"] for component in breakdown)

        return max(0, min(100, round(total)))

    def build_breakdown(
        self,
        nlp_score: float,
        vision_score: float,
        representation_score: float | None = None
    ) -> list[dict]:
        scores = {
            "nlp": nlp_score,
            "vision": vision_score
        }

        if representation_score is not None:
            scores["representation"] = representation_score

        active_weights = {
            name: COMPONENT_WEIGHTS[name]
            for name in scores
        }
        weight_total = sum(active_weights.values())

        breakdown = []

        for name, score in scores.items():
            normalized_weight = active_weights[name] / weight_total
            contribution = score * normalized_weight

            breakdown.append({
                "component": name,
                "score": round(score, 2),
                "weight": round(normalized_weight, 4),
                "contribution": round(contribution, 2)
            })

        return breakdown

    def explain_breakdown(self, breakdown: list[dict]) -> list[str]:
        explanations = []

        for component in breakdown:
            label = COMPONENT_LABELS.get(
                component["component"],
                component["component"]
            )

            explanations.append(
                f"{label} obtient {component['score']}/100 et pese "
                f"{round(component['weight'] * 100)}% du score final, "
                f"soit une contribution de {component['contribution']} points."
            )

        return explanations

    def calculate_nlp_penalty(
        self,
        total_paragraphs: int,
        issues_count: int
    ) -> float:
        if total_paragraphs == 0:
            return 0.0

        issue_ratio = issues_count / total_paragraphs

        return round(issue_ratio * 100, 2)

    def calculate_vision_penalty(
        self,
        images_analyzed: int,
        images_with_people: int
    ) -> float:
        if images_analyzed == 0:
            return 0.0

        representation_ratio = (
            images_with_people / images_analyzed
        )

        return round((1 - representation_ratio) * 100, 2)

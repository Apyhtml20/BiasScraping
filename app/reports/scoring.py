class InclusivityScorer:
    def calculate_overall_score(
        self,
        nlp_score: float,
        vision_score: float
    ) -> int:
        score = (
            nlp_score * 0.6
            + vision_score * 0.4
        )

        return max(0, min(100, round(score)))

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
from app.scraping_system.article_extractor import Article
from app.nlp.preprocessing import TextPreprocessor
from app.nlp.classifier import BiasClassifier

class NLPAnalyzer:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.classifier = BiasClassifier()

    def analyze(self, article: Article) -> dict:
        issues = []

        for paragraph in article.paragraphs:
            text = self.preprocessor.clean(paragraph.text)

            if not text:
                continue

            result = self.classifier.classify(text)

            if result["label"] != "neutral_inclusive":
                issues.append({
                    "paragraph_id": paragraph.id,
                    "text": text,
                    "type": result["label"],
                    "confidence": result["confidence"],
                    "severity": self.get_severity(result["confidence"])
                })

        return {
            "module": "nlp",
            "paragraphs_analyzed": len(article.paragraphs),
            "issues": issues,
            "score": self.calculate_score(
                len(article.paragraphs),
                len(issues)
            )
        }

    def get_severity(self, confidence: float) -> str:
        if confidence >= 0.85:
            return "high"

        if confidence >= 0.65:
            return "medium"

        return "low"

    def calculate_score(
        self,
        total_paragraphs: int,
        issues_count: int
    ) -> int:
        if total_paragraphs == 0:
            return 0

        score = 100 - (
            issues_count / total_paragraphs * 100
        )

        return max(0, round(score))
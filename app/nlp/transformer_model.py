from transformers import pipeline

LABELS = [
    "neutral_inclusive",
    "gendered_language",
    "gender_stereotype",
    "exclusionary_language",
    "potential_bias"
]

class TransformerModel:
    def __init__(self):
        self.model = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

    def predict(self, text: str) -> dict:
        result = self.model(
            text,
            candidate_labels=LABELS,
            multi_label=False
        )

        return {
            "label": result["labels"][0],
            "confidence": round(result["scores"][0], 4)
        }
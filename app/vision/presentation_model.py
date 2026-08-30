from transformers import pipeline

CANDIDATE_LABELS = [
    "a photo of a person with a feminine visual presentation",
    "a photo of a person with a masculine visual presentation",
    "a photo of a person with an androgynous or gender-neutral visual presentation",
]

LABEL_TO_CATEGORY = {
    CANDIDATE_LABELS[0]: "feminine_presenting",
    CANDIDATE_LABELS[1]: "masculine_presenting",
    CANDIDATE_LABELS[2]: "androgynous_presenting",
}


class PresentationModel:
    """Zero-shot CLIP classifier over perceived visual presentation.

    This estimates surface-level visual presentation signals only. It does
    not identify a person's actual sex or gender identity.
    """

    def __init__(self):
        self.model = pipeline(
            "zero-shot-image-classification",
            model="openai/clip-vit-base-patch32"
        )

    def predict(self, face_image) -> dict:
        results = self.model(
            face_image,
            candidate_labels=CANDIDATE_LABELS
        )

        scores = {
            LABEL_TO_CATEGORY[result["label"]]: round(result["score"], 4)
            for result in results
        }

        best_category = max(scores, key=scores.get)

        return {
            "best_category": best_category,
            "confidence": scores[best_category],
            "scores": scores
        }

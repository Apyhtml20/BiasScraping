import math

IDENTIFIED_CATEGORIES = [
    "feminine_presenting",
    "masculine_presenting",
    "androgynous_presenting",
]
ALL_CATEGORIES = IDENTIFIED_CATEGORIES + ["undetermined"]

# Diversity/balance are meaningless statistics on a handful of faces
# (e.g. a single portrait scoring 0 for "no diversity"), so the score
# is only computed once there is a large enough sample.
MIN_FACES_FOR_SCORE = 3


class RepresentationAggregator:
    """Aggregates per-face presentation signals into page-level diversity
    and balance statistics."""

    def aggregate(self, faces: list[dict]) -> dict:
        total_faces = len(faces)

        counts = {category: 0 for category in ALL_CATEGORIES}
        for face in faces:
            counts[face["category"]] += 1

        if total_faces == 0:
            return {
                "faces_detected": 0,
                "category_counts": counts,
                "category_ratios": {c: 0.0 for c in ALL_CATEGORIES},
                "diversity_index": None,
                "balance_index": None,
                "representation_score": None
            }

        category_ratios = {
            category: round(count / total_faces, 4)
            for category, count in counts.items()
        }

        if total_faces < MIN_FACES_FOR_SCORE:
            return {
                "faces_detected": total_faces,
                "category_counts": counts,
                "category_ratios": category_ratios,
                "diversity_index": None,
                "balance_index": None,
                "representation_score": None,
                "note": (
                    f"Fewer than {MIN_FACES_FOR_SCORE} faces detected; "
                    "diversity/balance score not computed on a sample "
                    "this small."
                )
            }

        diversity_index = self._normalized_entropy(
            counts,
            total_faces,
            len(ALL_CATEGORIES)
        )

        identified_counts = {
            category: counts[category]
            for category in IDENTIFIED_CATEGORIES
        }
        identified_total = sum(identified_counts.values())

        balance_index = self._normalized_entropy(
            identified_counts,
            identified_total,
            len(IDENTIFIED_CATEGORIES)
        )

        representation_score = round(
            ((diversity_index + balance_index) / 2) * 100
        )

        return {
            "faces_detected": total_faces,
            "category_counts": counts,
            "category_ratios": category_ratios,
            "diversity_index": round(diversity_index, 4),
            "balance_index": round(balance_index, 4),
            "representation_score": representation_score
        }

    def _normalized_entropy(
        self,
        counts: dict,
        total: int,
        num_categories: int
    ) -> float:
        if total == 0 or num_categories < 2:
            return 0.0

        entropy = 0.0

        for count in counts.values():
            if count == 0:
                continue

            probability = count / total
            entropy -= probability * math.log2(probability)

        max_entropy = math.log2(num_categories)

        return entropy / max_entropy if max_entropy > 0 else 0.0

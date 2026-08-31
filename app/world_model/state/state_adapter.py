from .state_schema import BiasState


def clamp(value: float) -> float:

    return max(
        0.0,
        min(1.0, float(value)),
    )


def score_to_unit(value):

    if value is None:
        return None

    return clamp(float(value) / 100.0)


def safe_ratio(
    numerator,
    denominator,
):

    if not denominator:

        return 0.0

    return clamp(
        float(numerator)
        / float(denominator)
    )


def results_to_state(
    report: dict,
) -> BiasState:

    summary = report.get(
        "summary",
        {},
    )

    representation = report.get(
        "representation",
        {},
    )

    metadata = report.get(
        "metadata",
        {},
    )

    # NLP

    nlp_health = score_to_unit(
        summary.get(
            "nlp_score",
            50,
        )
    )

    if nlp_health is None:

        nlp_health = 0.5


    # Vision

    vision_health = score_to_unit(
        summary.get(
            "vision_score",
            50,
        )
    )

    if vision_health is None:

        vision_health = 0.5


    # Representation

    representation_score = (
        summary.get(
            "representation_score"
        )
    )

    if representation_score is None:

        representation_score = (
            representation.get(
                "representation_score"
            )
        )


    if representation_score is None:

        representation_balance = 0.5

    else:

        representation_balance = (
            score_to_unit(
                representation_score
            )
        )


    # Diversity

    diversity_index = (
        representation.get(
            "diversity_index"
        )
    )


    if diversity_index is None:

        diversity = 0.5

    else:

        diversity = clamp(
            diversity_index
        )


    # People / Images ratio

    people_image_ratio = safe_ratio(

        representation.get(
            "images_with_faces",
            0,
        ),

        metadata.get(
            "images_analyzed",
            0,
        ),
    )


    # Inclusivity

    inclusivity = score_to_unit(

        report.get(
            "inclusivity_score",
            50,
        )
    )


    return BiasState(

        nlp_health=nlp_health,

        vision_health=vision_health,

        representation_balance=
            representation_balance,

        people_image_ratio=
            people_image_ratio,

        diversity=diversity,

        inclusivity=inclusivity,
    )
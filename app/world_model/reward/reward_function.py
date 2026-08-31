from ..state.state_schema import BiasState

# All BiasState fields are "0 = mauvais, 1 = bon" (see state_schema.py),
# so the reward is simply a weighted sum of increases across every
# dimension - unlike an earlier version of this function, no dimension
# is treated as "lower is better".
WEIGHTS = {
    "nlp_health": 1.5,
    "vision_health": 1.0,
    "representation_balance": 1.25,
    "people_image_ratio": 0.75,
    "diversity": 1.5,
    "inclusivity": 2.5,
}


def calculate_reward(
    current_state,
    action,
    next_state,
):
    """
    Reward = weighted sum of the improvement (next - current) across
    every BiasState dimension. `inclusivity` and `diversity` carry the
    highest weights since they're the composite goals of an audit;
    `action` is currently unused (no action-specific shaping) but kept
    in the signature for future use (e.g. penalizing "expensive" edits).
    """

    current = BiasState.from_list(list(current_state))
    future = BiasState.from_list(list(next_state))

    reward = sum(
        weight * (getattr(future, field) - getattr(current, field))
        for field, weight in WEIGHTS.items()
    )

    return float(reward)

def rollout(
    env,
    first_action,
):
    """
    Effectue une simulation d'une action.

    Retourne :
    - future state
    - reward
    """

    env.reset()

    next_state, reward, terminated, truncated, info = (
        env.step(first_action)
    )

    return {

        "action": int(first_action),

        "future_state": (
            next_state.tolist()
        ),

        "reward": float(reward),

        "terminated": terminated,

        "truncated": truncated,
    }
from ..actions.action_space import (
    ACTION_DESCRIPTIONS,
    ACTION_NAMES,
    BiasAction,
)
from ..state.state_schema import BiasState


def render_world_model_report(
    initial_state,
    planning_result,
):

    current = BiasState.from_list(
        initial_state
    )

    future = BiasState.from_list(
        planning_result[
            "best_future_state"
        ]
    )

    action = BiasAction(
        planning_result[
            "best_action"
        ]
    )

    return {

        "current_state": current.to_dict(),

        "recommended_action": {
            "id": int(action),

            "name": ACTION_NAMES[action],

            "description": (
                ACTION_DESCRIPTIONS[action]
            ),
        },

        "predicted_future_state": (
            future.to_dict()
        ),

        "expected_reward": (
            planning_result[
                "best_reward"
            ]
        ),

        "improvement": {

            "nlp_health": (
                future.nlp_health
                - current.nlp_health
            ),

            "vision_health": (
                future.vision_health
                - current.vision_health
            ),

            "representation_balance": (
                future.representation_balance
                - current.representation_balance
            ),

            "people_image_ratio": (
                future.people_image_ratio
                - current.people_image_ratio
            ),

            "diversity": (
                future.diversity
                - current.diversity
            ),

            "inclusivity": (
                future.inclusivity
                - current.inclusivity
            ),
        },

        "rollouts": (
            planning_result[
                "all_rollouts"
            ]
        ),
    }
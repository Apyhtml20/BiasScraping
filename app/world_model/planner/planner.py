from .rollout import rollout


class WorldModelPlanner:

    def __init__(self, env):

        self.env = env

    def plan(self):

        results = []

        action_count = (
            self.env.action_space.n
        )

        for action in range(action_count):

            result = rollout(
                self.env,
                action,
            )

            results.append(result)

        best_result = max(
            results,
            key=lambda x: x["reward"],
        )

        return {

            "best_action": (
                best_result["action"]
            ),

            "best_future_state": (
                best_result["future_state"]
            ),

            "best_reward": (
                best_result["reward"]
            ),

            "all_rollouts": results,
        }
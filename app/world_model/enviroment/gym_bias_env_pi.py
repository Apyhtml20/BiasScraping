import gymnasium as gym
import numpy as np
from gymnasium import spaces

from ..reward.reward_function import calculate_reward


class BiasScrapingEnv(gym.Env):

    metadata = {
        "render_modes": ["human"]
    }

    def __init__(
        self,
        simulator,
        initial_state,
        max_steps: int = 3,
    ):

        super().__init__()

        self.simulator = simulator

        self.initial_state = np.array(
            initial_state,
            dtype=np.float32,
        )

        self.current_state = self.initial_state.copy()

        self.max_steps = max_steps

        self.current_step = 0

        self.action_space = spaces.Discrete(4)

        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(6,),
            dtype=np.float32,
        )

    def reset(
        self,
        seed=None,
        options=None,
    ):

        super().reset(seed=seed)

        self.current_state = (
            self.initial_state.copy()
        )

        self.current_step = 0

        info = {}

        return (
            self.current_state,
            info,
        )

    def step(
        self,
        action,
    ):

        next_state = self.simulator.predict(
            self.current_state,
            int(action),
        )

        reward = calculate_reward(
            self.current_state,
            action,
            next_state,
        )

        self.current_state = np.array(
            next_state,
            dtype=np.float32,
        )

        self.current_step += 1

        terminated = False

        truncated = (
            self.current_step
            >= self.max_steps
        )

        info = {
            "action": int(action),
            "reward": reward,
        }

        return (
            self.current_state,
            reward,
            terminated,
            truncated,
            info,
        )
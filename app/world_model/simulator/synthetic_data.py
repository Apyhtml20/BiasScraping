import json
from pathlib import Path

import numpy as np

from ..actions.action_space import BiasAction
from ..state.state_logger import DEFAULT_LOG_PATH as REAL_STATES_PATH
from ..state.state_schema import BiasState

# No real (state, action, next_state) transitions exist yet - a genuine
# transition dataset would require running two audits of the same page
# before/after a real content edit, for every action, at scale. Nothing
# in the pipeline applies actions to content yet, so instead:
#
#   - the STARTING state of each synthetic sample is resampled (with
#     replacement, plus a little jitter) from real states logged by
#     state_logger.log_state() after every real /api/audit call, once
#     enough of them exist - falling back to uniform random sampling
#     otherwise. This keeps the training distribution grounded in
#     what BiasScraping actually sees in production, even though the
#     transitions themselves are still heuristic.
#   - each action then pushes a subset of state dimensions toward 1.0
#     with diminishing returns (`STRENGTH * (1 - current_value)`),
#     leaving the rest to drift only by noise;
#   - `inclusivity` is NOT an independent heuristic: it's recomputed
#     from the perturbed nlp/vision/representation values using the
#     exact same weights as InclusivityScorer (app/reports/scoring.py),
#     so the world model's notion of inclusivity matches the real score.
#
# Swap the action-effect step out for real observed transitions once
# there's a way to know which action was actually applied between two
# audits of the same page.

NOISE_STD = 0.02
REAL_STATE_JITTER_STD = 0.03
MIN_REAL_STATES_TO_USE = 5

INCLUSIVITY_WEIGHTS = {
    "nlp_health": 0.5,
    "vision_health": 0.25,
    "representation_balance": 0.25,
}

# field -> strength of the push toward 1.0 for that action
ACTION_EFFECTS = {
    BiasAction.REDUCE_LANGUAGE_BIAS: {
        "nlp_health": 0.35,
    },
    BiasAction.DIVERSIFY_SOURCES: {
        "diversity": 0.35,
        "representation_balance": 0.1,
    },
    BiasAction.ADD_BALANCED_VIEWPOINT: {
        "nlp_health": 0.15,
        "diversity": 0.2,
    },
    BiasAction.IMPROVE_VISUAL_REPRESENTATION: {
        "vision_health": 0.2,
        "representation_balance": 0.35,
        "people_image_ratio": 0.25,
        "diversity": 0.1,
    },
}

STATE_FIELDS = [
    "nlp_health",
    "vision_health",
    "representation_balance",
    "people_image_ratio",
    "diversity",
    "inclusivity",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _apply_action(
    state: dict,
    action: BiasAction,
    rng: np.random.Generator,
) -> dict:
    effects = ACTION_EFFECTS[action]
    next_state = {}

    for field in STATE_FIELDS:
        if field == "inclusivity":
            continue

        current_value = state[field]
        strength = effects.get(field, 0.0)
        push = strength * (1.0 - current_value)
        noise = rng.normal(0.0, NOISE_STD)

        next_state[field] = _clamp(current_value + push + noise)

    next_state["inclusivity"] = _clamp(
        sum(
            weight * next_state[field]
            for field, weight in INCLUSIVITY_WEIGHTS.items()
        )
        + rng.normal(0.0, NOISE_STD)
    )

    return next_state


def _load_real_states(path: Path) -> list[dict]:
    if not path.exists():
        return []

    states = []

    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            states.append(json.loads(line)["state"])

    return states


def _sample_starting_state(
    real_states: list[dict],
    rng: np.random.Generator,
) -> dict:
    if len(real_states) >= MIN_REAL_STATES_TO_USE:
        picked = real_states[int(rng.integers(0, len(real_states)))]

        return {
            field: _clamp(
                float(picked[field])
                + rng.normal(0.0, REAL_STATE_JITTER_STD)
            )
            for field in STATE_FIELDS
        }

    raw_state = {
        field: float(rng.uniform(0.0, 1.0))
        for field in STATE_FIELDS
        if field != "inclusivity"
    }
    raw_state["inclusivity"] = _clamp(
        sum(
            weight * raw_state[field]
            for field, weight in INCLUSIVITY_WEIGHTS.items()
        )
    )

    return raw_state


def generate_transitions(
    num_samples: int,
    seed: int = 0,
    real_states_path: Path = REAL_STATES_PATH,
):
    """Returns (states, actions, next_states) as numpy arrays, ready
    for train_world_model(). Starting states are resampled from real
    audits logged at `real_states_path` once there are at least
    MIN_REAL_STATES_TO_USE of them, otherwise drawn uniformly at
    random."""

    rng = np.random.default_rng(seed)
    actions = list(BiasAction)
    real_states = _load_real_states(real_states_path)

    states = np.zeros((num_samples, len(STATE_FIELDS)), dtype=np.float32)
    action_ids = np.zeros((num_samples,), dtype=np.int64)
    next_states = np.zeros((num_samples, len(STATE_FIELDS)), dtype=np.float32)

    for i in range(num_samples):
        raw_state = _sample_starting_state(real_states, rng)

        action = actions[int(rng.integers(0, len(actions)))]
        next_raw_state = _apply_action(raw_state, action, rng)

        state = BiasState(**raw_state)
        next_state = BiasState(**next_raw_state)

        states[i] = state.to_list()
        action_ids[i] = int(action)
        next_states[i] = next_state.to_list()

    return states, action_ids, next_states

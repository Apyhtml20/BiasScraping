import json
from datetime import UTC, datetime
from pathlib import Path

from .state_adapter import results_to_state

DEFAULT_LOG_PATH = Path("data/world_model/states.jsonl")


def log_state(
    url: str,
    report: dict,
    log_path: Path = DEFAULT_LOG_PATH,
) -> None:
    """Appends the real, observed BiasState from one audit to a growing
    dataset (JSONL, one observation per line).

    This only records the state actually seen in production - no action
    or next_state, since nothing in the pipeline applies an action to
    content yet (auditing is read-only). Training later resamples these
    real starting points instead of drawing them uniformly at random;
    see synthetic_data.py.
    """

    state = results_to_state(report)

    log_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "url": url,
        "timestamp": datetime.now(UTC).isoformat(),
        "state": state.to_dict(),
    }

    with open(log_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")

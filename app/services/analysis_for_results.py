from pathlib import Path

from app.world_model.enviroment.gym_bias_env_pi import (
    BiasScrapingEnv,
)
from app.world_model.planner.planner import (
    WorldModelPlanner,
)
from app.world_model.renderer.report_rendere import (
    render_world_model_report,
)
from app.world_model.simulator.simulator import (
    WorldModelSimulator,
)
from app.world_model.state.state_adapter import (
    results_to_state,
)


def run_world_model(
    analysis_results: dict,
):

    # 1. Analysis Results → State
    state = results_to_state(
        analysis_results
    )

    initial_state = state.to_list()

    # 2. Load PyTorch World Model
    model_path = Path(
        "models/world_model/dynamics_model.pt"
    )

    simulator = WorldModelSimulator(
        state_dim=6,
        action_dim=4,
        model_path=(
            str(model_path)
            if model_path.exists()
            else None
        ),
    )

    # 3. Create Gymnasium Environment
    env = BiasScrapingEnv(
        simulator=simulator,
        initial_state=initial_state,
    )

    # 4. Planning
    planner = WorldModelPlanner(env)

    planning_result = planner.plan()

    # 5. Renderer
    report = render_world_model_report(
        initial_state,
        planning_result,
    )

    return report
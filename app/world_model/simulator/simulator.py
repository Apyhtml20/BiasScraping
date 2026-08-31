import torch
import torch.nn.functional as F

from .dynamics_model_WM import DynamicsModel


class WorldModelSimulator:

    def __init__(
        self,
        state_dim: int = 6,
        action_dim: int = 4,
        model_path: str | None = None,
    ):

        self.state_dim = state_dim
        self.action_dim = action_dim

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model = DynamicsModel(
            state_dim=state_dim,
            action_dim=action_dim,
        ).to(self.device)

        if model_path:

            checkpoint = torch.load(
                model_path,
                map_location=self.device,
            )

            self.model.load_state_dict(checkpoint)

        self.model.eval()

    def predict(
        self,
        state,
        action: int,
    ):

        state_tensor = torch.tensor(
            state,
            dtype=torch.float32,
            device=self.device,
        ).unsqueeze(0)

        action_tensor = torch.tensor(
            [action],
            dtype=torch.long,
            device=self.device,
        )

        action_one_hot = F.one_hot(
            action_tensor,
            num_classes=self.action_dim,
        ).float()

        with torch.no_grad():

            next_state = self.model(
                state_tensor,
                action_one_hot,
            )

        return (
            next_state
            .squeeze(0)
            .cpu()
            .numpy()
        )
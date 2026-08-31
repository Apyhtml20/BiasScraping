import torch
from torch import nn


class DynamicsModel(nn.Module):
    """
    World Model Dynamics.
    Apprend la transition :
        State_t + Action_t -> State_t+1
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dim: int = 128
    ):
        super().__init__()

        input_dim = state_dim + action_dim

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),

            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),

            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),

            nn.Linear(hidden_dim, state_dim),
            nn.Sigmoid()
        )

    def forward(
        self,
        state: torch.Tensor,
        action: torch.Tensor
    ) -> torch.Tensor:

        # Combine state + action
        x = torch.cat(
            [state, action],
            dim=-1
        )

        # Predict future state
        next_state = self.network(x)

        return next_state
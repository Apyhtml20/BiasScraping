import os
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

import wandb

from .dynamics_model_WM import DynamicsModel
from .synthetic_data import generate_transitions

DEFAULT_CHECKPOINT_PATH = Path("models/world_model/dynamics_model.pt")


def train_world_model(
    states,
    actions,
    next_states,
    epochs=100,
    batch_size=32,
    learning_rate=0.001,
    use_wandb=True,
):

    state_dim = states.shape[1]

    action_dim = int(
        actions.max()
    ) + 1

    states_tensor = torch.tensor(
        states,
        dtype=torch.float32,
    )

    actions_tensor = torch.tensor(
        actions,
        dtype=torch.long,
    )

    next_states_tensor = torch.tensor(
        next_states,
        dtype=torch.float32,
    )

    dataset = TensorDataset(
        states_tensor,
        actions_tensor,
        next_states_tensor,
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
    )

    model = DynamicsModel(
        state_dim=state_dim,
        action_dim=action_dim,
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate,
    )

    criterion = nn.MSELoss()

    run = None

    if use_wandb:
        # Without WANDB_API_KEY, wandb's default "online" mode falls
        # back to an interactive login prompt - which hangs forever in
        # a non-interactive run. Default to "offline" (logs saved
        # locally under ./wandb/, syncable later with `wandb sync`)
        # unless a key or an explicit WANDB_MODE is already set.
        wandb_mode = os.environ.get("WANDB_MODE") or (
            "online" if os.environ.get("WANDB_API_KEY") else "offline"
        )

        run = wandb.init(
            project="biasscraping-world-model",
            mode=wandb_mode,
            config={
                "state_dim": state_dim,
                "action_dim": action_dim,
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "num_samples": states.shape[0],
            },
        )

    model.train()

    for epoch in range(epochs):

        total_loss = 0.0

        for (
            batch_states,
            batch_actions,
            batch_next_states,
        ) in loader:

            action_one_hot = (
                torch.nn.functional.one_hot(
                    batch_actions,
                    num_classes=action_dim,
                )
                .float()
            )

            predictions = model(
                batch_states,
                action_one_hot,
            )

            loss = criterion(
                predictions,
                batch_next_states,
            )

            optimizer.zero_grad()

            loss.backward()

            optimizer.step()

            total_loss += loss.item()

        epoch_loss = total_loss / len(loader)

        print(
            f"Epoch {epoch + 1}/{epochs} "
            f"Loss: "
            f"{epoch_loss:.6f}"
        )

        if run is not None:
            run.log(
                {
                    "epoch": epoch + 1,
                    "loss": epoch_loss,
                }
            )

    if run is not None:
        run.summary["final_loss"] = epoch_loss
        run.finish()

    return model


if __name__ == "__main__":
    states, actions, next_states = generate_transitions(
        num_samples=20000,
    )

    model = train_world_model(
        states,
        actions,
        next_states,
    )

    DEFAULT_CHECKPOINT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    torch.save(
        model.state_dict(),
        DEFAULT_CHECKPOINT_PATH,
    )

    print(f"Saved checkpoint to {DEFAULT_CHECKPOINT_PATH}")

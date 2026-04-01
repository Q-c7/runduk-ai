import logging
import os
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm


def train_epoch(model, train_dl, criterion, optimizer, device: str) -> list[float]:
    loss_log = []
    model.train()
    optimizer.zero_grad()

    for X, y in tqdm(train_dl, total=len(train_dl), desc="Train"):
        if isinstance(X, torch.Tensor):
            X = X.to(device)
        else:
            X = tuple(t.to(device) for t in X)

        output = model(X)
        loss = criterion(output, y.to(device).reshape(-1))
        loss_log.append(loss.detach().cpu().item())

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    return loss_log


@torch.inference_mode()
def evaluate(model, test_dl, device: str) -> float:
    correct = 0
    model.eval()

    for X, y in tqdm(test_dl, total=len(test_dl), desc="Val"):
        if isinstance(X, torch.Tensor):
            X = X.to(device)
        else:
            X = tuple(t.to(device) for t in X)

        outputs = model(X)
        labels = y.to(device).reshape(-1)
        correct += (torch.argmax(outputs, dim=-1) == labels).detach().cpu().sum()

    return correct / len(test_dl.dataset)


def save_plots(epoch_losses: list[float], epoch_accs: list[list[float]], plot_dir: str) -> None:
    import matplotlib.pyplot as plt

    os.makedirs(plot_dir, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    ax1.plot(epoch_losses)
    ax1.set_title("Train loss per epoch")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")

    if epoch_accs:
        accs_np = np.asarray(epoch_accs)
        for idx in range(accs_np.shape[1]):
            ax2.plot(accs_np[:, idx], label=f"Test set {idx}")

    ax2.set_title("Test accuracy (%)")
    ax2.set_xlabel("Epoch")
    ax2.legend()

    path = os.path.join(plot_dir, "training_curves.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logging.info(f"Saved training plots to {path}")


def run_training(
    model,
    name: str,
    train_data,
    test_datas: list,
    criterion,
    optimizer,
    epochs: int = 10,
    batch_size: int = 512,
    device: str = "cuda",
    plot_dir: str | None = None,
) -> None:
    torch.manual_seed(3407)

    train_dl = DataLoader(train_data, shuffle=True, batch_size=batch_size, num_workers=8)
    test_dls = [
        DataLoader(td, shuffle=False, batch_size=batch_size, num_workers=8)
        for td in test_datas
    ]

    epoch_losses: list[float] = []
    epoch_accs: list[list[float]] = []

    model = model.to(device)

    try:
        for epoch in range(epochs):
            logging.info(f"Epoch {epoch + 1}/{epochs}")

            loss_log = train_epoch(model, train_dl, criterion, optimizer, device)
            mean_loss = float(np.mean(loss_log))
            epoch_losses.append(mean_loss)

            accs = [evaluate(model, dl, device) * 100 for dl in test_dls]
            epoch_accs.append([float(a) for a in accs])

            acc_str = ", ".join(f"{a:.2f}%" for a in accs)
            logging.info(f"  loss={mean_loss:.4f}  acc=[{acc_str}]")

        _save_model(model, name)

    except KeyboardInterrupt:
        logging.warning("Training interrupted")
        _save_model(model, f"{name}-tmp")

    if plot_dir:
        save_plots(epoch_losses, epoch_accs, plot_dir)


def _save_model(model, name: str) -> None:
    pth_path = f"{name}.pth"
    raw_path = f"{name}.raw_model"

    torch.save(model.state_dict(), pth_path)
    logging.info(f"Saved state_dict to {pth_path}")

    torch.save(model, raw_path)
    logging.info(f"Saved full model to {raw_path}")

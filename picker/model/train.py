import json
import logging
import os
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm


def _to_device(X, device):
    if isinstance(X, torch.Tensor):
        return X.to(device)
    return tuple(t.to(device) for t in X)


@torch.inference_mode()
def evaluate(model, test_dl, device: str) -> float:
    correct = 0
    model.eval()

    for X, y in tqdm(test_dl, total=len(test_dl), desc="Val"):
        X = _to_device(X, device)
        outputs = model(X)
        labels = y.to(device).reshape(-1)
        correct += (torch.argmax(outputs, dim=-1) == labels).detach().cpu().sum()

    return correct / len(test_dl.dataset)


def save_plots(
    epoch_losses: list[float],
    eval_accs: list[list[float]],
    plot_dir: str,
    step_losses: list[float] | None = None,
    checkpoint_steps: list[int] | None = None,
    epoch_end_steps: list[int] | None = None,
    eval_steps: list[int] | None = None,
) -> None:
    import matplotlib.pyplot as plt

    os.makedirs(plot_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(24, 6))
    ckpt_steps = checkpoint_steps or []
    ep_steps = epoch_end_steps or []

    if step_losses:
        axes[0].plot(step_losses, alpha=0.3, linewidth=0.5)
        window = min(100, len(step_losses))
        if len(step_losses) >= window:
            smoothed = np.convolve(step_losses, np.ones(window) / window, mode="valid")
            axes[0].plot(range(window - 1, len(step_losses)), smoothed, linewidth=1.5)
        for s in ckpt_steps:
            axes[0].axvline(x=s, color="red", alpha=0.4, linewidth=0.8, linestyle="--")
    axes[0].set_title("Train loss per step")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Loss")

    if epoch_losses and ep_steps:
        axes[1].plot(
            ep_steps[: len(epoch_losses)], epoch_losses, marker="o", markersize=3
        )
    elif epoch_losses:
        axes[1].plot(epoch_losses, marker="o", markersize=3)
    for s in ckpt_steps:
        axes[1].axvline(x=s, color="red", alpha=0.4, linewidth=0.8, linestyle="--")
    axes[1].set_title("Train loss per epoch")
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("Loss")

    ev_steps = eval_steps or []
    if eval_accs:
        accs_np = np.asarray(eval_accs)
        x = ev_steps[: len(eval_accs)] if ev_steps else list(range(len(eval_accs)))
        for idx in range(accs_np.shape[1]):
            axes[2].plot(
                x, accs_np[:, idx], marker="o", markersize=3, label=f"Test set {idx}"
            )
    for s in ckpt_steps:
        axes[2].axvline(x=s, color="red", alpha=0.4, linewidth=0.8, linestyle="--")
    axes[2].set_title("Test accuracy (%)")
    axes[2].set_xlabel("Step")
    axes[2].legend()

    path = os.path.join(plot_dir, "training_curves.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    import json

    metrics = {
        "current_step": len(step_losses) if step_losses else 0,
        "epochs_completed": len(epoch_losses),
        "evals_completed": len(eval_accs) if eval_accs else 0,
        "epoch_losses": dict(zip(ep_steps[: len(epoch_losses)], epoch_losses))
        if ep_steps
        else {},
        "eval_accs": {
            s: {f"test_{i}": a for i, a in enumerate(accs)}
            for s, accs in zip(ev_steps[: len(eval_accs)], eval_accs)
        }
        if eval_accs and ev_steps
        else {},
        "checkpoint_steps": ckpt_steps,
    }
    json_path = os.path.join(plot_dir, "metrics.json")
    with open(json_path, "w") as f:
        json.dump(metrics, f, indent=2)

    logging.info(f"Saved plots to {path}, metrics to {json_path}")


class CheckpointManager:
    def __init__(self, checkpoint_dir: str, max_keep: int = 10):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.max_keep = max_keep
        self.checkpoint_steps: list[int] = []
        self._saved: list[Path] = sorted(
            self.checkpoint_dir.glob("step_*.pt"),
            key=lambda p: p.stat().st_mtime,
        )

    def save(
        self,
        model,
        optimizer,
        epoch: int,
        global_step: int,
        epoch_losses: list[float],
        eval_accs: list[list[float]],
        step_losses: list[float] | None = None,
        epoch_end_steps: list[int] | None = None,
        eval_steps: list[int] | None = None,
    ) -> Path:
        self.checkpoint_steps.append(global_step)
        path = self.checkpoint_dir / f"step_{global_step:08d}.pt"
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "epoch": epoch,
                "global_step": global_step,
                "epoch_losses": epoch_losses,
                "eval_accs": eval_accs,
                "eval_steps": eval_steps or [],
                "step_losses": step_losses or [],
                "checkpoint_steps": self.checkpoint_steps,
                "epoch_end_steps": epoch_end_steps or [],
            },
            path,
        )
        self._saved.append(path)
        logging.info(f"Checkpoint saved: {path}")

        while len(self._saved) > self.max_keep:
            old = self._saved.pop(0)
            old.unlink(missing_ok=True)
            logging.debug(f"Removed old checkpoint: {old}")

        return path

    @staticmethod
    def load(path: str | Path, model, optimizer, device: str) -> dict:
        ckpt = torch.load(path, map_location=device, weights_only=True)
        model.load_state_dict(ckpt["model_state_dict"])
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
        logging.info(
            f"Resumed from {path} (epoch {ckpt['epoch']}, step {ckpt['global_step']})"
        )
        return ckpt


def _mean_val_metric(last_eval_accs: list[float]) -> float:
    return float(sum(last_eval_accs) / len(last_eval_accs))


class EarlyStopping:
    """Track validation accuracy; stop when it fails to improve for `patience` evals."""

    def __init__(
        self,
        patience: int,
        min_delta: float,
        checkpoint_dir: Path,
        *,
        resume: bool,
    ) -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.checkpoint_dir = checkpoint_dir
        self.best_metric = float("-inf")
        self.best_state: dict[str, torch.Tensor] | None = None
        self.best_step = 0
        self._counter = 0
        self._enabled = patience > 0

        if self._enabled and resume:
            self._load_snapshot()

    def _paths(self) -> tuple[Path, Path]:
        return (
            self.checkpoint_dir / "early_stopping.json",
            self.checkpoint_dir / "best.pt",
        )

    def _load_snapshot(self) -> None:
        meta_path, best_path = self._paths()
        if not meta_path.is_file() or not best_path.is_file():
            return
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            self.best_metric = float(meta["best_metric"])
            self.best_step = int(meta["best_step"])
            self._counter = int(meta.get("patience_counter", 0))
            self.best_state = torch.load(
                best_path, map_location="cpu", weights_only=True
            )
            logging.info(
                f"Early stopping: restored best metric {self.best_metric:.4f}% "
                f"at step {self.best_step}, patience counter {self._counter}"
            )
        except (OSError, json.JSONDecodeError, KeyError) as e:
            logging.warning(f"Could not load early stopping state: {e}")

    def _persist(self) -> None:
        meta_path, best_path = self._paths()
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        with open(meta_path, "w") as f:
            json.dump(
                {
                    "best_metric": self.best_metric,
                    "best_step": self.best_step,
                    "patience_counter": self._counter,
                },
                f,
                indent=2,
            )
        if self.best_state is not None:
            torch.save(self.best_state, best_path)

    def step(
        self, model: torch.nn.Module, global_step: int, last_eval_accs: list[float]
    ) -> bool:
        """Return True if training should stop (overfitting / no val gain)."""
        if not self._enabled:
            return False

        m = _mean_val_metric(last_eval_accs)
        if m > self.best_metric + self.min_delta:
            self.best_metric = m
            self.best_step = global_step
            self._counter = 0
            self.best_state = {
                k: v.detach().cpu().clone() for k, v in model.state_dict().items()
            }
            self._persist()
            logging.info(
                f"  Early stopping: new best val mean acc {m:.4f}% (min_delta={self.min_delta})"
            )
            return False

        self._counter += 1
        logging.info(
            f"  Early stopping: no val improvement ({self._counter}/{self.patience})"
        )
        self._persist()
        return self._counter >= self.patience

    def restore_best(self, model: torch.nn.Module, device: str) -> None:
        if self.best_state is not None:
            model.load_state_dict(self.best_state)
            model.to(device)
            logging.info(
                f"Restored best weights from step {self.best_step} "
                f"(val mean acc {self.best_metric:.4f}%)"
            )


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
    checkpoint_dir: str = "checkpoints",
    checkpoint_every: int = 500,
    max_checkpoints: int = 10,
    resume: str | None = None,
    early_stopping_patience: int = 0,
    early_stopping_min_delta: float = 0.01,
) -> None:
    torch.manual_seed(3407)

    train_dl = DataLoader(
        train_data, shuffle=True, batch_size=batch_size, num_workers=8
    )
    test_dls = [
        DataLoader(td, shuffle=False, batch_size=batch_size, num_workers=8)
        for td in test_datas
    ]

    epoch_losses: list[float] = []
    epoch_end_steps: list[int] = []
    eval_accs: list[list[float]] = []
    eval_steps: list[int] = []
    step_losses: list[float] = []
    start_epoch = 0
    global_step = 0

    model = model.to(device)
    ckpt_mgr = CheckpointManager(checkpoint_dir, max_keep=max_checkpoints)

    if resume:
        ckpt = ckpt_mgr.load(resume, model, optimizer, device)
        start_epoch = ckpt["epoch"] + 1
        global_step = ckpt["global_step"]
        epoch_losses = ckpt.get("epoch_losses", [])
        epoch_end_steps = ckpt.get("epoch_end_steps", [])
        eval_accs = ckpt.get("eval_accs", ckpt.get("epoch_accs", []))
        eval_steps = ckpt.get("eval_steps", ckpt.get("epoch_end_steps", []))
        step_losses = ckpt.get("step_losses", [])

    es: EarlyStopping | None = None
    if early_stopping_patience > 0:
        es = EarlyStopping(
            patience=early_stopping_patience,
            min_delta=early_stopping_min_delta,
            checkpoint_dir=Path(checkpoint_dir),
            resume=bool(resume),
        )

    def _evaluate_and_log():
        accs = [evaluate(model, dl, device) * 100 for dl in test_dls]
        eval_accs.append([float(a) for a in accs])
        eval_steps.append(global_step)
        acc_str = ", ".join(f"{a:.2f}%" for a in accs)
        logging.info(f"  [step {global_step}] acc=[{acc_str}]")

    def _checkpoint(run_eval: bool = True) -> bool:
        stop = False
        if run_eval:
            _evaluate_and_log()
            if es is not None and eval_accs:
                stop = es.step(model, global_step, eval_accs[-1])
        ckpt_mgr.save(
            model,
            optimizer,
            epoch,
            global_step,
            epoch_losses,
            eval_accs,
            step_losses,
            epoch_end_steps,
            eval_steps,
        )
        if plot_dir:
            save_plots(
                epoch_losses,
                eval_accs,
                plot_dir,
                step_losses,
                ckpt_mgr.checkpoint_steps,
                epoch_end_steps,
                eval_steps,
            )
        return stop

    try:
        stopped_early = False
        for epoch in range(start_epoch, epochs):
            logging.info(f"Epoch {epoch + 1}/{epochs}")
            model.train()
            optimizer.zero_grad()
            loss_log = []

            for X, y in tqdm(train_dl, total=len(train_dl), desc="Train"):
                X = _to_device(X, device)
                output = model(X)
                loss = criterion(output, y.to(device).reshape(-1))
                step_loss = loss.detach().cpu().item()
                loss_log.append(step_loss)
                step_losses.append(step_loss)

                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

                global_step += 1
                if global_step % checkpoint_every == 0:
                    if _checkpoint():
                        stopped_early = True
                        break

            if stopped_early:
                break

            mean_loss = float(np.mean(loss_log))
            epoch_losses.append(mean_loss)
            epoch_end_steps.append(global_step)
            logging.info(f"  loss={mean_loss:.4f}")

            if _checkpoint():
                stopped_early = True
                break

        if es is not None:
            es.restore_best(model, device)
        if stopped_early:
            logging.info(
                "Stopped early: validation accuracy did not improve (overfitting guard)."
            )
        _save_model(model, name)

    except KeyboardInterrupt:
        logging.warning("Training interrupted — saving checkpoint")
        _checkpoint()
        _save_model(model, f"{name}-interrupted")

    if plot_dir:
        save_plots(
            epoch_losses,
            eval_accs,
            plot_dir,
            step_losses,
            ckpt_mgr.checkpoint_steps,
            epoch_end_steps,
            eval_steps,
        )


def _save_model(model, name: str) -> None:
    pth_path = f"{name}.pth"
    raw_path = f"{name}.raw_model"

    torch.save(model.state_dict(), pth_path)
    logging.info(f"Saved state_dict to {pth_path}")

    torch.save(model, raw_path)
    logging.info(f"Saved full model to {raw_path}")

# THIS CODE WAS NOT USED IN SOTA VERSION

import matplotlib.pyplot as plt
import numpy as np
import torch
from IPython.core.display_functions import clear_output
from torch.utils.data import DataLoader
from tqdm import tqdm


def train(model, train_dl, criterion, optimizer, device: str = "cuda:1") -> list[float]:
    loss_log = []
    model.train()
    optimizer.zero_grad()

    for idx, (X, y) in enumerate(tqdm(train_dl, total=len(train_dl), desc="Train...")):
        X = X.to(device)
        output = model(X)
        loss = criterion(
            output,
            y.to(device).reshape(
                -1,
            ),
        )
        loss_log.append(loss.detach().cpu().numpy().item())

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

    return loss_log


@torch.inference_mode()
def test(model, test_dl, device: str = "cuda:1") -> float:
    correct = 0
    model.eval()
    for idx, (X, y) in enumerate(tqdm(test_dl, total=len(test_dl), desc="Val...")):
        outputs = model(X.to(device))
        labels = y.to(device).reshape(
            -1,
        )
        correct += (torch.argmax(outputs, dim=-1) == labels).detach().cpu().sum()

    return correct / len(test_dl.dataset)


def plot_stuff(losses, accs):
    figsize = (16, 6)
    f, axarr = plt.subplots(1, 2, figsize=figsize)
    ax1, ax2 = axarr

    ax1.plot(losses)
    ax1.set_title("Losses on train")

    ax2.plot(accs)
    ax2.set_title("Accs on test")

    plt.show()


def run_training(
    model,
    name,
    train_data,
    test_data,
    criterion,
    epochs: int = 10,
    lr: float = 3e-4,
    batch_size: int = 512,
    device: str = "cuda:1",
):
    torch.manual_seed(3407)

    train_dl = DataLoader(
        train_data, shuffle=True, batch_size=batch_size, num_workers=8
    )
    test_dl = DataLoader(test_data, shuffle=False, batch_size=batch_size, num_workers=8)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    plot_stuff(losses=[], accs=[])

    epoch_losses = []
    epoch_accs = []

    model = model.to(device)

    for epoch in range(epochs):
        loss_log = train(
            model=model,
            train_dl=train_dl,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
        )
        epoch_losses.append(np.mean(loss_log))

        acc = test(model=model, test_dl=test_dl, device=device) * 100
        epoch_accs.append(acc)

        clear_output()
        plot_stuff(losses=epoch_losses, accs=epoch_accs)

        if epoch % 10 == 0:
            torch.save(model.state_dict(), f"{name}.pth")
            print(f"saved model to `{name}.pth` after {epoch + 1} epochs")

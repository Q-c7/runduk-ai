import argparse
import logging

import polars as pl
import torch
from torch.nn import CrossEntropyLoss

from picker.model.constants import HERO_TRANSFORM
from picker.model.dataset import TeamDataset
from picker.model.train import run_training
from picker.model.transformer import TransformerModel


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the Dota 2 draft prediction model"
    )
    parser.add_argument(
        "--data", type=str, required=True, help="Path to preprocessed parquet file"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="latest",
        help="Model name for saved files (default: latest)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Number of training epochs (default: 100)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=8192, help="Batch size (default: 8192)"
    )
    parser.add_argument(
        "--lr", type=float, default=3e-4, help="Learning rate (default: 3e-4)"
    )
    parser.add_argument(
        "--device", type=str, default="cuda", help="Device (default: cuda)"
    )
    parser.add_argument(
        "--num-layers",
        type=int,
        default=6,
        help="Transformer encoder layers (default: 6)",
    )
    parser.add_argument(
        "--num-heads", type=int, default=8, help="Attention heads (default: 8)"
    )
    parser.add_argument(
        "--dropout", type=float, default=0.1, help="Dropout (default: 0.1)"
    )
    parser.add_argument(
        "--hero-emb-dim",
        type=int,
        default=28,
        help="Hero embedding dimension (default: 28)",
    )
    parser.add_argument(
        "--rank-emb-dim",
        type=int,
        default=3,
        help="Rank embedding dimension (default: 3)",
    )
    parser.add_argument(
        "--mask-p",
        type=float,
        default=0.2,
        help="Hero masking probability during training (default: 0.2)",
    )
    parser.add_argument(
        "--test-split",
        type=float,
        default=0.05,
        help="Fraction of data for test set (default: 0.05)",
    )
    parser.add_argument(
        "--plot-dir",
        type=str,
        default=None,
        help="Directory to save training plots (optional)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    logging.info(f"Loading data from {args.data}")
    df = pl.read_parquet(args.data)
    dicts = df.to_dicts()

    split_idx = len(dicts) - len(dicts) // int(1 / args.test_split)
    train_dicts = dicts[:split_idx]
    test_dicts = dicts[split_idx:]
    logging.info(f"Train: {len(train_dicts)} samples, Test: {len(test_dicts)} samples")

    train_data = TeamDataset(path="", dicts_override=train_dicts, p=args.mask_p)
    test_data_clean = TeamDataset(path="", dicts_override=test_dicts, p=0.0)
    test_data_masked = TeamDataset(path="", dicts_override=test_dicts, p=args.mask_p)

    num_heroes = len(HERO_TRANSFORM) + 1
    embedding_dict = {
        "team": [num_heroes, args.hero_emb_dim],
        "rank": [6, args.rank_emb_dim],
    }

    model = TransformerModel(
        embedding_dict=embedding_dict,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        dropout=args.dropout,
    )
    logging.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    run_training(
        model=model,
        name=args.name,
        train_data=train_data,
        test_datas=[test_data_clean, test_data_masked],
        criterion=CrossEntropyLoss(),
        optimizer=torch.optim.Adam(model.parameters(), lr=args.lr),
        epochs=args.epochs,
        batch_size=args.batch_size,
        device=args.device,
        plot_dir=args.plot_dir,
    )


if __name__ == "__main__":
    main()

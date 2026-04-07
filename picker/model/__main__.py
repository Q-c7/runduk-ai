import argparse
import logging
from pathlib import Path

import polars as pl
import torch
import yaml
from torch.nn import CrossEntropyLoss

from picker.model.constants import HERO_TRANSFORM
from picker.model.dataset import TeamDataset
from picker.model.train import run_training
from picker.model.transformer import TransformerModel

DEFAULT_CONFIG = Path(__file__).parent / "default_config.yaml"


def load_config(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the Dota 2 draft prediction model"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="YAML config file (default: built-in default_config.yaml)",
    )
    parser.add_argument(
        "--data", type=str, required=True, help="Path to preprocessed parquet file"
    )
    parser.add_argument(
        "--plot-dir", type=str, default=None, help="Directory to save training plots"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )

    parser.add_argument("--name", type=str)
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--lr", type=float)
    parser.add_argument("--device", type=str)
    parser.add_argument("--num-layers", type=int)
    parser.add_argument("--num-heads", type=int)
    parser.add_argument("--d-model", type=int)
    parser.add_argument("--dropout", type=float)
    parser.add_argument("--hero-emb-dim", type=int)
    parser.add_argument("--rank-emb-dim", type=int)
    parser.add_argument("--mask-p", type=float)
    parser.add_argument("--test-split", type=float)
    parser.add_argument("--label-smoothing", type=float)
    parser.add_argument("--checkpoint-dir", type=str)
    parser.add_argument("--checkpoint-every", type=int)
    parser.add_argument("--max-checkpoints", type=int)
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Path to checkpoint .pt file to resume from",
    )
    parser.add_argument(
        "--init-weights",
        type=str,
        default=None,
        help="Path to a .pth state_dict for fine-tuning (fresh optimizer, epoch 0). "
        "Mutually exclusive with --resume.",
    )
    parser.add_argument(
        "--early-stopping-patience",
        type=int,
        help="Stop after this many val evals without improvement (0 = off). "
        "Also writes best.pt in checkpoint-dir.",
    )
    parser.add_argument(
        "--early-stopping-min-delta",
        type=float,
        help="Minimum mean val acc improvement (%%) to reset patience.",
    )

    args, _ = parser.parse_known_args()
    cfg = load_config(args.config)

    parser.set_defaults(**cfg)
    args = parser.parse_args()

    if args.resume and args.init_weights:
        parser.error("Use either --resume or --init-weights, not both.")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    logging.info(f"Config: {args.config}")
    logging.info(f"Loading data from {args.data}")
    df = pl.read_parquet(args.data)

    split_idx = len(df) - len(df) // int(1 / args.test_split)
    train_df = df[:split_idx]
    test_df = df[split_idx:]
    del df
    logging.info(f"Train: {len(train_df)} samples, Test: {len(test_df)} samples")

    train_data = TeamDataset(df=train_df, p=args.mask_p)
    test_data_clean = TeamDataset(df=test_df, p=0.0)
    test_data_masked = TeamDataset(df=test_df, p=args.mask_p)

    num_heroes = len(HERO_TRANSFORM) + 1
    embedding_dict = {
        "team": [num_heroes, args.hero_emb_dim],
        "rank": [6, args.rank_emb_dim],
    }

    model = TransformerModel(
        embedding_dict=embedding_dict,
        d_model=args.d_model,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        dropout=args.dropout,
    )
    logging.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    if args.init_weights:
        sd = torch.load(args.init_weights, map_location="cpu", weights_only=True)
        model.load_state_dict(sd)
        logging.info(f"Loaded initial weights from {args.init_weights} (fine-tuning)")

    run_training(
        model=model,
        name=args.name,
        train_data=train_data,
        test_datas=[test_data_clean, test_data_masked],
        criterion=CrossEntropyLoss(label_smoothing=args.label_smoothing),
        optimizer=torch.optim.Adam(model.parameters(), lr=args.lr),
        epochs=args.epochs,
        batch_size=args.batch_size,
        device=args.device,
        plot_dir=args.plot_dir,
        checkpoint_dir=args.checkpoint_dir,
        checkpoint_every=args.checkpoint_every,
        max_checkpoints=args.max_checkpoints,
        resume=args.resume,
        early_stopping_patience=args.early_stopping_patience,
        early_stopping_min_delta=args.early_stopping_min_delta,
    )


if __name__ == "__main__":
    main()

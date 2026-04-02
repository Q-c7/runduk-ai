import logging

import polars as pl

from picker.scraping.constants import RELEVANT_GAME_MODES

MAX_RANK_BUCKET = 5


def preprocess(
    input_path: str,
    output_path: str,
    game_modes: set[int] | None = None,
) -> pl.DataFrame:
    if game_modes is None:
        game_modes = RELEVANT_GAME_MODES

    logging.info(f"Reading raw data from {input_path}")
    df = pl.read_parquet(input_path)
    logging.info(f"Loaded {len(df)} rows")

    df = df.filter(
        pl.col("game_mode").is_in(list(game_modes)),
        pl.col("avg_rank_tier").is_not_null(),
        pl.col("radiant_team").list.len() == 5,
        pl.col("dire_team").list.len() == 5,
    )
    logging.info(f"{len(df)} rows after filtering to game modes {game_modes}")

    df = df.with_columns(
        (pl.col("avg_rank_tier").cast(pl.Int64) // 10 - 1)
        .clip(0, MAX_RANK_BUCKET)
        .alias("avg_rank_tier"),
        pl.when("radiant_win")
        .then("radiant_team")
        .otherwise("dire_team")
        .alias("winner_team"),
        pl.when("radiant_win")
        .then("dire_team")
        .otherwise("radiant_team")
        .alias("loser_team"),
    ).drop(["dire_team", "radiant_team", "radiant_win"])

    df.write_parquet(output_path)
    logging.info(f"Saved {len(df)} processed rows to {output_path}")
    return df

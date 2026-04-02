from __future__ import annotations

import numpy as np
import torch
import polars as pl
from numpy.typing import NDArray
from torch.utils.data import Dataset

from picker.model.constants import HERO_TRANSFORM

_TRANSFORM_TABLE = np.zeros(max(HERO_TRANSFORM.keys()) + 1, dtype=np.int64)
for _api_id, _dense_id in HERO_TRANSFORM.items():
    _TRANSFORM_TABLE[_api_id] = _dense_id


def _hero_lists_to_array(col: pl.Series) -> NDArray[np.int64]:
    """Convert a column of 5-element hero-id lists to (N, 5) int64 array,
    mapping API hero ids to dense indices via HERO_TRANSFORM."""
    raw = col.list.to_array(5).to_numpy().astype(np.int64)
    return _TRANSFORM_TABLE[raw]


class TeamDataset(Dataset):
    def __init__(
        self,
        path: str = "",
        df: pl.DataFrame | None = None,
        p: float = 0.2,
        give_rank: bool = True,
    ):
        if df is None:
            df = pl.read_parquet(path)

        df = df.filter(
            pl.col("winner_team").list.len() == 5,
            pl.col("loser_team").list.len() == 5,
        )

        self.winners = _hero_lists_to_array(df["winner_team"])
        self.losers = _hero_lists_to_array(df["loser_team"])
        self.ranks = df["avg_rank_tier"].to_numpy().astype(np.int64)
        self._n = len(df)

        self.p = p
        self.give_rank = give_rank

    def __len__(self) -> int:
        return self._n * 2

    def _transform_teams(self, team_a: NDArray, team_b: NDArray, rank: int):
        tensor = torch.from_numpy(np.concatenate((team_a, team_b)))
        if self.give_rank:
            return tensor * (torch.rand(10) >= self.p), torch.tensor(rank)
        else:
            return tensor * (torch.rand(10) >= self.p)

    def __getitem__(self, idx):  # type: ignore[override]  # ty: ignore[invalid-method-override]
        row = idx // 2
        rank = self.ranks[row]
        if idx % 2 == 0:
            return self._transform_teams(self.winners[row], self.losers[row], rank), 1
        else:
            return self._transform_teams(self.losers[row], self.winners[row], rank), 0

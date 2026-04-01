import torch
import polars as pl
from torch.utils.data import Dataset

from picker.model.constants import HERO_TRANSFORM


class TeamDataset(Dataset):
    def __init__(
        self, path: str, dicts_override: list[dict] | None = None, p: float = 0.2, give_rank: bool = True
    ):
        if dicts_override is not None:
            self.dicts = dicts_override
        else:
            df = pl.read_parquet(path)
            self.dicts = df.to_dicts()

        self.p = p
        self.give_rank = give_rank

    def __len__(self):
        return len(self.dicts) * 2

    def _transform_teams(self, team_a: list, team_b: list, rank: int):
        tensor = torch.cat(
            (
                torch.as_tensor([HERO_TRANSFORM[h] for h in team_a]),
                torch.as_tensor([HERO_TRANSFORM[h] for h in team_b]),
            )
        )
        if self.give_rank:
            return tensor * (torch.rand(10) >= self.p), torch.tensor(rank)
        else:
            return tensor * (torch.rand(10) >= self.p)

    def __getitem__(self, idx):
        dict_idx = idx // 2
        dict_with_info = self.dicts[dict_idx]
        winner, loser = dict_with_info["winner_team"], dict_with_info["loser_team"]
        rank = dict_with_info["avg_rank_tier"]
        if idx % 2 == 0:
            return self._transform_teams(winner, loser, rank), 1
        else:
            return self._transform_teams(loser, winner, rank), 0

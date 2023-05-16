# SOTA MODEL

from typing import Any

import torch
import torch.nn as nn
from torch import Tensor
from torch.nn import TransformerEncoder, TransformerEncoderLayer


class TransformerModel(nn.Module):
    SEQ_LEN = 10

    def __init__(
        self,
        embedding_dict: dict[str, Any],
        num_layers: int = 4,
        num_heads: int = 8,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.model_type = "Transformer"
        self.embeddings = nn.ModuleDict(
            {
                key: nn.Embedding(*embed_args, padding_idx=0)
                for key, embed_args in embedding_dict.items()
            }
        )

        assert "team" in self.embeddings.keys(), "Please provide hero embedding"
        assert "rank" in self.embeddings.keys(), "Please provide rank embedding"

        self.hidden_dim = (
            self.embeddings["team"].embedding_dim
            + 1
            + self.embeddings["rank"].embedding_dim
        )

        self.cls_vector = nn.Parameter(torch.rand(self.hidden_dim, requires_grad=True))

        self.encoder = TransformerEncoder(
            TransformerEncoderLayer(
                d_model=self.hidden_dim,
                dim_feedforward=self.hidden_dim * 4,
                nhead=num_heads,
                batch_first=True,
                dropout=dropout,
            ),
            num_layers=num_layers,
            norm=nn.LayerNorm([self.SEQ_LEN + 1, self.hidden_dim]),
        )

        self.head = nn.Sequential(
            nn.Flatten(),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, 2),
        )

    def _prepare(self, src: Tensor, rank: Tensor, device: str = "cpu"):
        team_embs = torch.cat(
            (
                torch.ones(src.shape[0], 5, 1, device=device),  # first 5 are Radiant
                -torch.ones(src.shape[0], 5, 1, device=device),
            ),  # then Dire
            dim=-2,
        )
        hero_embs = self.embeddings["team"](src)
        rank_embs = (
            self.embeddings["rank"](rank).repeat(1, 10).reshape(src.shape[0], 10, -1)
        )
        return torch.cat((hero_embs, team_embs, rank_embs), dim=-1)

    def forward(self, inputs_: tuple[Tensor, Tensor]) -> Tensor:
        src, rank = inputs_
        x = self._prepare(src, rank, device=src.device)

        x = torch.cat(
            (
                x,
                self.cls_vector.repeat(x.shape[0])
                .reshape(x.shape[0], x.shape[-1])
                .unsqueeze(1),
            ),
            dim=-2,
        )

        x = self.encoder(x)  # , src_key_padding_mask=mask

        cls_encoded = x[:, -1, :]

        return self.head(cls_encoded)

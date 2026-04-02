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
        d_model: int | None = None,
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

        team_emb = self.embeddings["team"]
        rank_emb = self.embeddings["rank"]
        assert isinstance(team_emb, nn.Embedding)
        assert isinstance(rank_emb, nn.Embedding)
        concat_dim = team_emb.embedding_dim + 1 + rank_emb.embedding_dim
        self.hidden_dim = d_model if d_model is not None else concat_dim

        self.input_proj = nn.Linear(concat_dim, self.hidden_dim)
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
            norm=nn.LayerNorm(self.hidden_dim),
        )

        self.head = nn.Sequential(
            nn.Linear(self.hidden_dim, self.hidden_dim * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(self.hidden_dim * 4, self.hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(self.hidden_dim, 2),
        )

    def _prepare(self, src: Tensor, rank: Tensor, device: str | torch.device = "cpu"):
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
        return self.input_proj(torch.cat((hero_embs, team_embs, rank_embs), dim=-1))

    def forward(self, inputs_: tuple[Tensor, Tensor]) -> Tensor:
        src, rank = inputs_
        x = self._prepare(src, rank, device=src.device)

        pad_mask = src == 0  # [batch, 10]
        cls_mask = torch.zeros(src.shape[0], 1, dtype=torch.bool, device=src.device)
        pad_mask = torch.cat((pad_mask, cls_mask), dim=1)  # [batch, 11]

        x = torch.cat(
            (
                x,
                self.cls_vector.view(1, 1, -1).expand(x.shape[0], -1, -1),
            ),
            dim=-2,
        )

        x = self.encoder(x, src_key_padding_mask=pad_mask)

        cls_encoded = x[:, -1, :]

        return self.head(cls_encoded)

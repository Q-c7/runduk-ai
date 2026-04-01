# THIS CODE WAS NOT USED IN SOTA VERSION

import torch
import torch.nn as nn

from torch import Tensor
from copy import deepcopy


class MLPWithEmbeddings(nn.Module):
    def __init__(self, embeds: nn.Embedding, create_unk_manually: bool = True):
        super().__init__()

        emb = deepcopy(embeds)
        emb.requires_grad_(False)
        if create_unk_manually:
            emb.weight[0] = emb.weight[1:].mean(axis=0)
        emb.weight = torch.nn.Parameter(
            torch.nn.functional.normalize(emb.weight), requires_grad=False
        )

        self.embs = emb
        embedding_dim = embeds.embedding_dim

        self.model = nn.Sequential(
            nn.Linear(2 * embedding_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 84),
            nn.ReLU(),
            nn.Linear(84, 64),
            nn.ReLU(),
            nn.Linear(64, 48),
            nn.ReLU(),
            nn.Linear(48, 16),
            nn.ReLU(),
            nn.Linear(16, 2),  # 2
        )

    def forward(self, ctx_heroes: Tensor):
        all_embeds = self.embs(ctx_heroes)
        assert all_embeds.shape[-2] == 10

        allied_emb = all_embeds[:, :5].mean(dim=-2)
        enemy_emb = all_embeds[:, 5:].mean(dim=-2)
        ctx = torch.cat((allied_emb, enemy_emb), dim=-1)  # BS, 2*emb_dim

        return self.model(ctx)

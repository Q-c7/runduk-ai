# THIS CODE WAS NOT USED IN SOTA VERSION

import torch
import torch.nn as nn

from torch import Tensor

from picker.model.constants import HERO_TRANSFORM

EMBEDDING_DIM = 16
EMBED_MAX_NORM = 1
VOCAB_SIZE = len(HERO_TRANSFORM) + 1


class CBOWModel(nn.Module):
    def __init__(
        self, vocab_size: int = VOCAB_SIZE, emdedding_dim: int = EMBEDDING_DIM
    ):
        super().__init__()
        self.t_embs = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=emdedding_dim,
            max_norm=EMBED_MAX_NORM,
        )
        self.c_embs = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=emdedding_dim,
            max_norm=EMBED_MAX_NORM,
        )

        # self.c_fc = nn.Sequential(
        #     nn.Linear(
        #         in_features=2 * emdedding_dim,
        #         out_features=emdedding_dim,
        #     )
        # )

        self.head = nn.Sequential(
            nn.Linear(
                in_features=2 * emdedding_dim,
                out_features=vocab_size,
            )
        )

    # def forward(self, heroes: Tensor):
    #     hero_emb = self.t_embs(heroes[:, :1]) # BS, 1, emb_dim
    #
    #     allied_emb = self.c_embs(heroes[:, 1:5]).mean(dim=-2)  # BS, 4, emb_dim -> BS, emb_dim
    #     enemy_emb = self.c_embs(heroes[:, 5:]).mean(dim=-2)
    #     ctx = self.c_fc(torch.cat((allied_emb, enemy_emb), dim=-1))  # BS, 2*emb_dim -> BS, emb_dim
    #
    #     dots = hero_emb.bmm(ctx[None]) # BS, 1, 1
    #     return dots.view(-1, 1)

    def forward(self, ctx_heroes: Tensor):
        all_embeds = self.t_embs(ctx_heroes)
        assert all_embeds.shape[-2] == 9

        allied_emb = all_embeds[:, :4].mean(dim=-2)  # BS, 4, emb_dim -> BS, emb_dim
        enemy_emb = all_embeds[:, 4:].mean(dim=-2)
        ctx = torch.cat((allied_emb, enemy_emb), dim=-1)  # BS, 2*emb_dim

        return self.head(ctx)

    def normalize_embeddings(self):
        embeddings = list(self.t_embs.parameters())[0]
        embeddings = embeddings.cpu().detach().numpy()
        norms = (embeddings**2).sum(axis=1) ** (1 / 2)
        norms = norms.reshape(norms.shape[0], 1)
        return embeddings / norms


# class CBOWLoss(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.torch_ce = nn.CrossEntropyLoss(reduction='sum')
#
#     def forward(self, hero, output, win):
#         logits, _, _, _ = output
#         if output2 is not None:
#             warnings.warn('wtf')
#         probs = torch.softmax(logits, dim=1)
#         return self.torch_ce(hero, output) * win

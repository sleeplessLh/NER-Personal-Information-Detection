"""Version 2: 在最小 Module 中加入 Embedding。"""

import torch
from torch import nn


class BiLSTMNER(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int = 64) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)

    def embed(self, input_ids: torch.Tensor) -> torch.Tensor:
        return self.embedding(input_ids)

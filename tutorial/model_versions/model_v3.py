"""Version 3: Embedding 后加入双向 LSTM。"""

import torch
from torch import nn


class BiLSTMNER(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int = 64, hidden_dim: int = 96) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            batch_first=True,
            bidirectional=True,
        )

    def encode(self, input_ids: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(input_ids)
        encoded, _ = self.lstm(embedded)
        return encoded

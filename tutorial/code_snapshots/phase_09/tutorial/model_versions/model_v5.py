"""Version 5: 实现标准 forward，支持 model(input_ids)。"""

import torch
from torch import nn


class BiLSTMNER(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        num_labels: int,
        embedding_dim: int = 64,
        hidden_dim: int = 96,
        dropout: float = 0.25,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim * 2, num_labels)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(input_ids)
        encoded, _ = self.lstm(embedded)
        return self.classifier(self.dropout(encoded))

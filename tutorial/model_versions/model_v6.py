"""Version 6: 与最终模型一致，加入四维大小写/数字特征。"""

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
        self.feature_projection = nn.Linear(4, 8)
        self.lstm = nn.LSTM(
            embedding_dim + 8,
            hidden_dim,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim * 2, num_labels)

    def forward(self, input_ids: torch.Tensor, features: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(input_ids)
        projected_features = torch.relu(self.feature_projection(features))
        combined = torch.cat([embedded, projected_features], dim=-1)
        encoded, _ = self.lstm(combined)
        return self.classifier(self.dropout(encoded))

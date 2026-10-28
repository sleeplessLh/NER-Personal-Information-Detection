"""从零实现 Embedding + BiLSTM + Linear 的 Token 分类模型。"""

from __future__ import annotations

import torch
from torch import nn


class BiLSTMNER(nn.Module):
    """根据每个 Token 的 ID、大小写特征，预测对应的 BIO 标签分数。"""

    def __init__(self, vocab_size: int, num_labels: int, embedding_dim: int = 64, hidden_dim: int = 96, dropout: float = 0.25):
        # 必须先初始化 nn.Module，PyTorch 才能登记下面各层的可训练参数。
        super().__init__()
        # 输入 Shape：(batch_size, sequence_length)
        # 输出 Shape：(batch_size, sequence_length, embedding_dim)
        # padding_idx=0 保证补齐位置的向量不参与正常词语学习。
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        # 每个 Token 有 4 个大小写/数字特征，先投影到 8 维。
        self.feature_projection = nn.Linear(4, 8)
        # BiLSTM 同时读取左到右和右到左的上下文。
        # 输出最后一维是 hidden_dim * 2，因为两个方向会拼接。
        self.lstm = nn.LSTM(
            embedding_dim + 8,
            hidden_dim,
            batch_first=True,
            bidirectional=True,
            num_layers=1,
        )
        # Dropout 只在训练模式随机屏蔽部分特征，降低过拟合。
        self.dropout = nn.Dropout(dropout)
        # 把每个 Token 的 192 维上下文表示映射为 num_labels 个 logits。
        self.classifier = nn.Linear(hidden_dim * 2, num_labels)

    def forward(self, input_ids: torch.Tensor, features: torch.Tensor) -> torch.Tensor:
        """执行前向传播，返回 Shape 为 (batch, length, num_labels) 的 logits。"""
        # 将整数 Token ID 查表转换为可训练的稠密向量。
        embedded = self.embedding(input_ids)
        # ReLU 把大小写特征变换为非线性表示。
        projected_features = torch.relu(self.feature_projection(features))
        # 在最后一维拼接词向量与大小写特征，不改变 batch 和 sequence 维度。
        combined = torch.cat([embedded, projected_features], dim=-1)
        # encoded 保存每个 Token 已融合双向上下文的 Hidden State。
        encoded, _ = self.lstm(combined)
        # 返回未经过 Softmax 的 logits；CrossEntropyLoss 会在内部处理 Softmax。
        return self.classifier(self.dropout(encoded))

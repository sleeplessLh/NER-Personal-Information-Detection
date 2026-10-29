"""Phase 10: 在四个 token 上完成一次真正的参数更新。"""

import torch
from torch import nn
from torch.optim import Adam

from src.model import BiLSTMNER


def main() -> None:
    torch.manual_seed(42)
    model = BiLSTMNER(vocab_size=12, num_labels=8, embedding_dim=8, hidden_dim=6)
    input_ids = torch.tensor([[2, 3, 4, 5]], dtype=torch.long)
    features = torch.zeros((1, 4, 4), dtype=torch.float32)
    labels = torch.tensor([[2, 3, 0, 0]], dtype=torch.long)
    optimizer = Adam(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    before = model.classifier.weight.detach().clone()

    optimizer.zero_grad()  # 清除上一轮梯度；本例是第一轮，但正式循环每轮都需要。
    logits = model(input_ids, features)
    loss = criterion(logits.reshape(-1, 8), labels.reshape(-1))
    loss.backward()  # 计算梯度，不在这一行更新参数。
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
    optimizer.step()  # Adam 根据梯度修改参数。

    print("logits shape:", tuple(logits.shape))
    print("loss:", round(loss.item(), 6))
    print("classifier changed:", not torch.equal(before, model.classifier.weight))
    assert logits.shape == (1, 4, 8)
    assert not torch.equal(before, model.classifier.weight)


if __name__ == "__main__":
    main()

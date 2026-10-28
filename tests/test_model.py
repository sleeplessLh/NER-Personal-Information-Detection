import torch

from src.model import BiLSTMNER


def test_forward_tensor_shape_and_gradient_flow():
    model = BiLSTMNER(vocab_size=20, num_labels=8, embedding_dim=16, hidden_dim=12)
    input_ids = torch.tensor([[2, 3, 0], [4, 5, 6]])
    features = torch.zeros((2, 3, 4))
    logits = model(input_ids, features)
    assert logits.shape == (2, 3, 8)
    logits.sum().backward()
    assert model.classifier.weight.grad is not None

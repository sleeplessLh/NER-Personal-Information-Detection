import importlib

import torch


def load(version: int):
    return importlib.import_module(f"tutorial.model_versions.model_v{version}")


def test_version_1_instantiates_module():
    assert isinstance(load(1).BiLSTMNER(), torch.nn.Module)


def test_version_2_embedding_shape():
    model = load(2).BiLSTMNER(vocab_size=20, embedding_dim=16)
    assert model.embed(torch.tensor([[2, 3, 0]])).shape == (1, 3, 16)


def test_version_3_bilstm_shape():
    model = load(3).BiLSTMNER(vocab_size=20, embedding_dim=16, hidden_dim=12)
    assert model.encode(torch.tensor([[2, 3, 0]])).shape == (1, 3, 24)


def test_version_4_classifier_shape_and_train_eval_dropout():
    model = load(4).BiLSTMNER(20, 8, embedding_dim=16, hidden_dim=12)
    assert model.classify(torch.tensor([[2, 3, 0]])).shape == (1, 3, 8)
    model.eval()
    assert not model.dropout.training


def test_version_5_standard_forward_and_gradient():
    model = load(5).BiLSTMNER(20, 8, embedding_dim=16, hidden_dim=12)
    logits = model(torch.tensor([[2, 3, 0]]))
    logits.sum().backward()
    assert logits.shape == (1, 3, 8)
    assert model.classifier.weight.grad is not None


def test_version_6_features_match_final_shape():
    model = load(6).BiLSTMNER(20, 8, embedding_dim=16, hidden_dim=12)
    logits = model(torch.tensor([[2, 3, 0]]), torch.zeros((1, 3, 4)))
    assert logits.shape == (1, 3, 8)

import torch
from torch import nn

from src.constants import LABELS, MALAYSIAN_DIR, MODELS_DIR, PROCESSED_DIR
from src.dataset import load_jsonl
from src.metrics import entity_metrics
from src.model import BiLSTMNER
from src.predict import Predictor
from src.redact import redact_text


def test_dataset_loading_and_malaysian_split_integrity():
    train = load_jsonl(PROCESSED_DIR / "train.jsonl")
    local_train = load_jsonl(MALAYSIAN_DIR / "train.jsonl")
    local_test = load_jsonl(MALAYSIAN_DIR / "test.jsonl")
    assert len(train) == 2400 and len(local_train) == 160 and len(local_test) == 60
    assert {row["text"].lower() for row in local_train}.isdisjoint(
        {row["text"].lower() for row in local_test}
    )


def test_single_training_step_updates_parameters():
    model = BiLSTMNER(vocab_size=12, num_labels=len(LABELS), embedding_dim=8, hidden_dim=6)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    inputs = torch.tensor([[2, 3, 4]])
    features = torch.zeros((1, 3, 4))
    labels = torch.tensor([[2, 1, 4]])
    before = model.classifier.weight.detach().clone()
    loss = nn.CrossEntropyLoss()(model(inputs, features).reshape(-1, len(LABELS)), labels.reshape(-1))
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    assert not torch.equal(before, model.classifier.weight.detach())


def test_checkpoint_can_be_saved_and_loaded(tmp_path):
    model = BiLSTMNER(vocab_size=10, num_labels=len(LABELS), embedding_dim=8, hidden_dim=6)
    path = tmp_path / "checkpoint.pt"
    torch.save(model.state_dict(), path)
    restored = BiLSTMNER(vocab_size=10, num_labels=len(LABELS), embedding_dim=8, hidden_dim=6)
    restored.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    assert torch.equal(model.classifier.weight, restored.classifier.weight)


def test_model_evaluation_counts_entity_boundaries():
    metrics = entity_metrics(
        [["B-PER", "O", "B-LOC"]],
        [["B-PER", "O", "B-ORG"]],
    )
    assert metrics["PER"]["f1"] == 1.0
    assert metrics["LOC"]["fn"] == 1
    assert metrics["ORG"]["fp"] == 1


def test_checkpoint_cpu_inference_and_end_to_end_redaction():
    predictor = Predictor(MODELS_DIR / "best_model.pt")
    assert next(predictor.model.parameters()).device.type == "cpu"
    result = predictor.predict("Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.")
    redacted = redact_text(result["text"], result["entities"])
    assert redacted == "[PER] studies at [ORG] in [LOC]."

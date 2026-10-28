"""训练 BiLSTM，以 Validation F1 选择最佳模型，并保存完整推理工件。"""

from __future__ import annotations

import argparse
import json
import random
import time

import numpy as np
import torch
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader

from .constants import LABELS, MODELS_DIR, PROCESSED_DIR, REPORTS_DIR, SEED
from .dataset import NERDataset, collate_batch, load_jsonl
from .metrics import entity_metrics
from .model import BiLSTMNER
from .preprocessing import build_vocabulary, save_json


def set_seed(seed: int) -> None:
    """固定 Python、NumPy、PyTorch 随机种子，尽可能提高可复现性。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_epoch(model, loader, criterion, device, optimizer=None):
    """运行一个训练或验证 Epoch；optimizer=None 表示只验证、不更新参数。"""
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    gold_sequences, predicted_sequences = [], []
    id_to_label = {index: label for index, label in enumerate(LABELS)}
    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        features = batch["features"].to(device)
        labels = batch["labels"].to(device)
        mask = batch["mask"].to(device)
        if training:
            # PyTorch 默认累积梯度，所以每个 Batch 开始前必须清空旧梯度。
            optimizer.zero_grad()
        # model(...) 会由 nn.Module 自动调用 BiLSTMNER.forward()。
        logits = model(input_ids, features)
        # CrossEntropyLoss 需要二维类别分数，因此把 Batch 和 Length 合并。
        loss = criterion(logits.reshape(-1, logits.shape[-1]), labels.reshape(-1))
        if training:
            # 从 Loss 反向计算每个可训练参数的 Gradient。
            loss.backward()
            # 避免 LSTM 梯度过大造成训练不稳定。
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            # Adam 根据刚才的 Gradient 更新模型参数；顺序不能提前。
            optimizer.step()
        total_loss += loss.item()
        predictions = logits.argmax(dim=-1)
        for row in range(labels.shape[0]):
            length = int(mask[row].sum().item())
            gold_sequences.append([id_to_label[int(value)] for value in labels[row, :length]])
            predicted_sequences.append([id_to_label[int(value)] for value in predictions[row, :length]])
    return total_loss / max(len(loader), 1), entity_metrics(gold_sequences, predicted_sequences)


def main() -> None:
    """命令行训练入口：加载数据、建立词表、训练、验证并保存 checkpoint。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.003)
    args = parser.parse_args()
    set_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_rows = load_jsonl(PROCESSED_DIR / "train.jsonl")
    validation_rows = load_jsonl(PROCESSED_DIR / "validation.jsonl")
    local_train_path = PROCESSED_DIR.parent / "malaysian" / "train.jsonl"
    local_validation_path = PROCESSED_DIR.parent / "malaysian" / "validation.jsonl"
    local_train_rows = load_jsonl(local_train_path) if local_train_path.exists() else []
    local_validation_rows = load_jsonl(local_validation_path) if local_validation_path.exists() else []
    train_rows.extend(local_train_rows)
    validation_rows.extend(local_validation_rows)
    vocabulary = build_vocabulary(row["tokens"] for row in train_rows)
    label_to_id = {label: index for index, label in enumerate(LABELS)}
    train_loader = DataLoader(NERDataset(train_rows, vocabulary, label_to_id, entity_word_dropout=0.8, general_word_dropout=0.15), batch_size=args.batch_size, shuffle=True, collate_fn=collate_batch)
    validation_loader = DataLoader(NERDataset(validation_rows, vocabulary, label_to_id), batch_size=args.batch_size, shuffle=False, collate_fn=collate_batch)

    config = {"embedding_dim": 64, "hidden_dim": 96, "dropout": 0.25}
    model = BiLSTMNER(len(vocabulary), len(LABELS), **config).to(device)
    # Padding 位置没有真实标签，ignore_index 保证它不贡献 Loss。
    criterion = nn.CrossEntropyLoss(ignore_index=label_to_id["<PAD>"])
    optimizer = Adam(model.parameters(), lr=args.learning_rate)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    best_f1 = -1.0
    history = []
    started = time.perf_counter()
    for epoch in range(1, args.epochs + 1):
        epoch_started = time.perf_counter()
        train_loss, train_metrics = run_epoch(model, train_loader, criterion, device, optimizer)
        with torch.no_grad():
            validation_loss, validation_metrics = run_epoch(model, validation_loader, criterion, device)
        record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "validation_loss": validation_loss,
            "validation_precision": validation_metrics["overall"]["precision"],
            "validation_recall": validation_metrics["overall"]["recall"],
            "validation_f1": validation_metrics["overall"]["f1"],
            "duration_seconds": time.perf_counter() - epoch_started,
        }
        history.append(record)
        print(json.dumps(record))
        if record["validation_f1"] > best_f1:
            # 只根据 Validation F1 选模；Test Set 不参与任何训练决策。
            best_f1 = record["validation_f1"]
            torch.save({
                "model_state_dict": model.state_dict(),
                "vocabulary": vocabulary,
                "labels": LABELS,
                "model_config": config,
                "preprocessing": {"lowercase_vocabulary": True, "casing_features": ["is_title", "is_upper", "is_lower", "has_digit"], "training_entity_word_dropout": 0.8, "training_general_word_dropout": 0.15},
                "dataset_counts": {"training": len(train_rows), "validation": len(validation_rows), "malaysian_training": len(local_train_rows), "malaysian_validation": len(local_validation_rows)},
                "seed": SEED,
                "best_epoch": epoch,
                "best_validation_f1": best_f1,
            }, MODELS_DIR / "best_model.pt")
    output = {"device": str(device), "total_duration_seconds": time.perf_counter() - started, "history": history}
    save_json(output, REPORTS_DIR / "training_log.json")
    print(f"Saved best model with validation F1={best_f1:.4f}")


if __name__ == "__main__":
    main()

"""把 JSONL 样本转换为 PyTorch Tensor，并把变长句子补齐为 Batch。"""

from __future__ import annotations

import json
from pathlib import Path

import torch
from torch.utils.data import Dataset

from .constants import LABELS
from .preprocessing import casing_features, tokens_to_ids


def load_jsonl(path: Path) -> list[dict]:
    """逐行读取 JSONL；每行代表一个已标注句子。"""
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


class NERDataset(Dataset):
    """让 DataLoader 可以按索引取得单条 NER 样本。"""
    def __init__(self, rows: list[dict], vocabulary: dict[str, int], label_to_id: dict[str, int], entity_word_dropout: float = 0.0, general_word_dropout: float = 0.0):
        self.rows = rows
        self.vocabulary = vocabulary
        self.label_to_id = label_to_id
        self.entity_word_dropout = entity_word_dropout
        self.general_word_dropout = general_word_dropout

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict:
        # input_ids Shape：(当前句子长度,)。训练时的 word dropout
        # 会把部分词替换成 <UNK>，迫使模型学习上下文而不是背记实体名称。
        row = self.rows[index]
        input_ids = torch.tensor(tokens_to_ids(row["tokens"], self.vocabulary), dtype=torch.long)
        if self.entity_word_dropout:
            for position, label in enumerate(row["labels"]):
                probability = self.entity_word_dropout if label != "O" else self.general_word_dropout
                if row["tokens"][position].isalnum() and torch.rand(()) < probability:
                    input_ids[position] = self.vocabulary["<UNK>"]
        return {
            "tokens": row["tokens"],
            "input_ids": input_ids,
            "features": torch.tensor(casing_features(row["tokens"]), dtype=torch.float32),
            "labels": torch.tensor([self.label_to_id[label] for label in row["labels"]], dtype=torch.long),
        }


def collate_batch(batch: list[dict]) -> dict:
    """把不同长度句子 Padding 到本 Batch 的最大长度。"""
    # 最终 input_ids/labels/mask Shape：(batch_size, max_length)
    # features Shape：(batch_size, max_length, 4)
    batch_size = len(batch)
    max_length = max(len(item["input_ids"]) for item in batch)
    input_ids = torch.zeros((batch_size, max_length), dtype=torch.long)
    features = torch.zeros((batch_size, max_length, 4), dtype=torch.float32)
    labels = torch.zeros((batch_size, max_length), dtype=torch.long)
    mask = torch.zeros((batch_size, max_length), dtype=torch.bool)
    tokens: list[list[str]] = []
    for row_index, item in enumerate(batch):
        length = len(item["input_ids"])
        input_ids[row_index, :length] = item["input_ids"]
        features[row_index, :length] = item["features"]
        labels[row_index, :length] = item["labels"]
        mask[row_index, :length] = True
        tokens.append(item["tokens"])
    return {"tokens": tokens, "input_ids": input_ids, "features": features, "labels": labels, "mask": mask}

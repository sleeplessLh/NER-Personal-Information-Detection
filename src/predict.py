"""加载自己训练的 checkpoint，对原始文本执行 NER 推理。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import torch

from .constants import MODELS_DIR
from .model import BiLSTMNER
from .preprocessing import casing_features, tokenize_with_spans, tokens_to_ids


@dataclass
class Predictor:
    """封装模型重建、Token 预测和实体抽取，供 CLI/API 复用。"""
    checkpoint_path: Path = MODELS_DIR / "best_model.pt"

    def __post_init__(self) -> None:
        # 避免 Windows CPU 推理时 OpenMP 线程过度订阅导致首次 forward 阻塞。
        torch.set_num_threads(1)
        # checkpoint 同时保存权重、Vocabulary、Label Mapping 和模型配置。
        checkpoint = torch.load(self.checkpoint_path, map_location="cpu", weights_only=False)
        self.vocabulary = checkpoint["vocabulary"]
        self.labels = checkpoint["labels"]
        self.model = BiLSTMNER(len(self.vocabulary), len(self.labels), **checkpoint["model_config"])
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

    def predict_tokens(self, tokens: list[str]) -> list[str]:
        """接收 Token 列表，返回等长的 BIO 标签列表。"""
        if not tokens:
            return []
        input_ids = torch.tensor([tokens_to_ids(tokens, self.vocabulary)], dtype=torch.long)
        features = torch.tensor([casing_features(tokens)], dtype=torch.float32)
        with torch.no_grad():
            # 推理不需要 Gradient；argmax 选择每个 Token 分数最高的标签。
            predictions = self.model(input_ids, features).argmax(dim=-1)[0]
        tags = [self.labels[int(index)] for index in predictions]
        # 纯标点不可能单独构成 PER/LOC/ORG。若模型把 `!` 等预测为 I-LOC，
        # 直接解码会吞掉标点并破坏实体 text 与字符 offset 的一致性。
        return [tag if re.search(r"\w", token, flags=re.UNICODE) else "O" for token, tag in zip(tokens, tags, strict=True)]

    def predict(self, text: str) -> dict:
        """接收原始字符串，返回 Token、BIO 标签和合并后的实体。"""
        tokens, token_spans = tokenize_with_spans(text)
        tags = self.predict_tokens(tokens)
        entities = extract_entities(tokens, tags, token_spans)
        return {"text": text, "tokens": tokens, "tags": tags, "entities": entities}


def extract_entities(
    tokens: list[str],
    tags: list[str],
    token_spans: list[tuple[int, int]] | None = None,
) -> list[dict]:
    """把连续 B/I 标签合并为带起止 Token 位置的实体字典。"""
    entities = []
    current = None
    for index, (token, tag) in enumerate(zip(tokens, tags, strict=True)):
        if tag.startswith("B-") or (tag.startswith("I-") and (current is None or current["type"] != tag[2:])):
            if current:
                entities.append(current)
            current = {"text": token, "type": tag[2:], "start_token": index, "end_token": index + 1}
        elif tag.startswith("I-") and current:
            current["text"] += " " + token
            current["end_token"] = index + 1
        else:
            if current:
                entities.append(current)
                current = None
    if current:
        entities.append(current)
    if token_spans is not None:
        for entity in entities:
            entity["start"] = token_spans[entity["start_token"]][0]
            entity["end"] = token_spans[entity["end_token"] - 1][1]
    return entities

"""文本分词、词表构建、BIO 标签校验与 Token ID 转换。"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from .constants import LABELS, PAD_TOKEN, UNK_TOKEN

TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\d+(?:[.,]\d+)*|[^\w\s]", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """按原顺序拆分英文单词、数字和标点，返回 Token 字符串列表。"""
    return TOKEN_PATTERN.findall(text)


def tokenize_with_spans(text: str) -> tuple[list[str], list[tuple[int, int]]]:
    """分词并返回每个 Token 在原始字符串中的字符区间 ``[start, end)``。"""
    matches = list(TOKEN_PATTERN.finditer(text))
    return [match.group(0) for match in matches], [match.span() for match in matches]


def normalize_token(token: str) -> str:
    """仅为查词表统一成小写；显示与大小写特征仍使用原始 Token。"""
    return token.lower()


def validate_bio(tokens: list[str], labels: list[str]) -> None:
    """检查 Token/Label 等长、标签合法，以及 I 标签必须跟在同类型实体后。"""
    if len(tokens) != len(labels):
        raise ValueError(f"Token/label length mismatch: {len(tokens)} != {len(labels)}")
    allowed = set(LABELS) - {"<PAD>"}
    previous_type: str | None = None
    for index, label in enumerate(labels):
        if label not in allowed:
            raise ValueError(f"Unknown label at {index}: {label}")
        if label == "O":
            previous_type = None
            continue
        prefix, entity_type = label.split("-", 1)
        if prefix == "I" and previous_type != entity_type:
            raise ValueError(f"Illegal I-tag at {index}: {label}")
        previous_type = entity_type


def build_vocabulary(sentences: Iterable[list[str]], min_frequency: int = 1) -> dict[str, int]:
    """从训练句子建立 token -> integer ID 的映射。"""
    counts = Counter(normalize_token(token) for sentence in sentences for token in sentence)
    vocabulary = {PAD_TOKEN: 0, UNK_TOKEN: 1}
    for token in sorted(counts):
        if counts[token] >= min_frequency:
            vocabulary[token] = len(vocabulary)
    return vocabulary


def tokens_to_ids(tokens: list[str], vocabulary: dict[str, int]) -> list[int]:
    """把 Token 转为 ID；未见过的词统一使用 <UNK> 的 ID。"""
    unknown_id = vocabulary[UNK_TOKEN]
    return [vocabulary.get(normalize_token(token), unknown_id) for token in tokens]


def casing_features(tokens: list[str]) -> list[list[float]]:
    """为每个 Token 返回 [首字母大写, 全大写, 全小写, 含数字] 四个特征。"""
    return [
        [float(t.istitle()), float(t.isupper()), float(t.islower()), float(any(c.isdigit() for c in t))]
        for t in tokens
    ]


def save_json(data: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))

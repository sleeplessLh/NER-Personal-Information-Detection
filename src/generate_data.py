"""生成来源透明的合成 NER 语料，并检查 Train/Validation/Test 句子泄漏。"""

from __future__ import annotations

import json
import random
from pathlib import Path

from .constants import MALAYSIAN_DIR, PROCESSED_DIR, SEED
from .preprocessing import tokenize, validate_bio

ENTITY_POOLS = {
    "train": {
        "PER": ["Aisha Rahman", "Daniel Wong", "Nur Izzati", "Michael Chen", "Priya Nair", "James Brown", "Emma Wilson", "Hafiz Omar", "Mei Lin", "Ravi Kumar", "Fatimah Zahra", "Lucas Martin"],
        "LOC": ["Penang", "Paris", "Tokyo", "Selangor", "Berlin", "Singapore", "Perak", "Sydney", "Sabah", "Dublin", "Manchester", "Putrajaya", "Kota Kinabalu", "Los Angeles", "Hong Kong", "George Town", "New Delhi", "Bandar Seri Begawan"],
        "ORG": ["Microsoft", "Universiti Malaya", "AirAsia", "Google", "Maybank", "World Health Organization", "Tesla", "Universiti Putra Malaysia", "Petronas", "Red Cross", "Intel", "CIMB Bank"],
    },
    "validation": {
        "PER": ["Siti Aminah", "Oliver Smith", "Tan Wei Ming", "Sophia Garcia"],
        "LOC": ["Kuala Lumpur", "London", "Johor Bahru", "Madrid"],
        "ORG": ["Universiti Kebangsaan Malaysia", "Amazon", "Bank Negara Malaysia", "Netflix"],
    },
    "test": {
        "PER": ["John Carter", "Ali Hassan", "Sarah Lee", "Ahmad Zaki", "Siti Hajar", "Grace Taylor"],
        "LOC": ["Edinburgh", "Bangkok", "Melbourne", "Malacca", "New York", "Kuching"],
        "ORG": ["Universiti Teknologi Malaysia", "Microsoft Research", "OpenAI", "Sunway University", "Apple", "Sarawak General Hospital"],
    },
}

TEMPLATES = [
    "{PER} lives in {LOC} .",
    "{PER} works at {ORG} in {LOC} .",
    "{PER} studies at {ORG} .",
    "Yesterday , {PER} visited {LOC} .",
    "{ORG} hired {PER} for its {LOC} office .",
    "A report from {ORG} was signed by {PER} .",
    "Please send the document to {PER} at {ORG} .",
    "The meeting between {PER} and {ORG} happened in {LOC} .",
    "{PER} moved from {LOC} to join {ORG} .",
    "After arriving in {LOC} , {PER} called {ORG} .",
    "{PER} met {PER2} at {ORG} .",
    "{PER} submitted the report .",
    "{PER} arrived early .",
    "The conference took place in {LOC} .",
    "{LOC} will host the next conference .",
    "{ORG} opened a laboratory .",
    "{ORG} hired a specialist .",
]
NO_ENTITY = {
    "train": [
        "Please review the attached report .", "The system completed the task successfully .",
        "The weather is pleasant today .", "The weather is rainy this morning .",
        "This document contains general information .", "A routine update will happen tomorrow .",
        "Our software processed the request correctly .", "Students submitted the assignment on time .",
        "The room is quiet and clean .", "No private details appear in this message .",
    ],
    "validation": ["A meeting will begin tomorrow morning .", "No private details appear here ."],
    "test": ["The weather is beautiful today .", "This ordinary sentence contains no entity ."],
}

MALAYSIAN_POOLS = {
    "train": {
        "PER": ["Ahmad Firdaus", "Nurul Aisyah", "Lim Wei Jian", "Arjun Nair", "Siti Khadijah", "Tan Jia Hui", "Muhammad Haziq", "Devi Krishnan"],
        "LOC": ["Shah Alam", "Ipoh", "Kuantan", "Seremban", "Alor Setar", "Kota Bharu", "Miri", "Cyberjaya"],
        "ORG": ["Petronas", "Maybank", "Telekom Malaysia", "Universiti Putra Malaysia", "Hospital Serdang", "Bank Negara Malaysia", "Tenaga Nasional", "CIMB Bank"],
    },
    "validation": {
        "PER": ["Farah Nabila", "Lee Jun Hao"],
        "LOC": ["Putrajaya", "Petaling Jaya"],
        "ORG": ["Universiti Kebangsaan Malaysia", "Hospital Putrajaya"],
    },
    "test": {
        "PER": ["Aina Sofea", "Kumar Raj", "Jason Teoh"],
        "LOC": ["George Town", "Johor Bahru", "Kuching"],
        "ORG": ["Universiti Sains Malaysia", "Hospital Kuala Lumpur", "Sarawak Energy"],
    },
}


def _annotate(rendered: str, values: dict[str, str]) -> dict[str, list[str]]:
    """根据已知合成实体位置创建 BIO 标签；仅用于生成训练数据。"""
    tokens = rendered.split()
    labels = ["O"] * len(tokens)
    for entity_type, value in values.items():
        entity_tokens = value.split()
        for start in range(len(tokens) - len(entity_tokens) + 1):
            if tokens[start : start + len(entity_tokens)] == entity_tokens:
                labels[start] = f"B-{entity_type}"
                for offset in range(1, len(entity_tokens)):
                    labels[start + offset] = f"I-{entity_type}"
                break
    validate_bio(tokens, labels)
    return {"tokens": tokens, "labels": labels, "text": " ".join(tokens)}


def generate_split(split: str, size: int, seed: int) -> list[dict[str, list[str]]]:
    """使用指定 split 的独立实体池生成固定数量样本。"""
    rng = random.Random(seed)
    pool = ENTITY_POOLS[split]
    rows: list[dict[str, list[str]]] = []
    for index in range(size):
        if index % 6 == 0:
            text = rng.choice(NO_ENTITY[split])
            rows.append(_annotate(text, {}))
            continue
        template = rng.choice(TEMPLATES)
        values = {kind: rng.choice(items) for kind, items in pool.items() if "{" + kind + "}" in template}
        annotations = dict(values)
        if "{PER2}" in template:
            values["PER2"] = rng.choice([name for name in pool["PER"] if name != values.get("PER")])
            annotations["PER_SECOND"] = values["PER2"]
        rendered = template.format(**values)
        annotation_types = {key: ("PER" if key == "PER_SECOND" else key) for key in annotations}
        typed_values = {annotation_types[key]: value for key, value in annotations.items() if key != "PER_SECOND"}
        row = _annotate(rendered, typed_values)
        if "PER_SECOND" in annotations:
            second = annotations["PER_SECOND"].split()
            for start in range(len(row["tokens"]) - len(second) + 1):
                if row["tokens"][start:start + len(second)] == second:
                    row["labels"][start] = "B-PER"
                    for offset in range(1, len(second)):
                        row["labels"][start + offset] = "I-PER"
                    break
            validate_bio(row["tokens"], row["labels"])
        rows.append(row)
    rng.shuffle(rows)
    return rows


def generate_malaysian_split(split: str, size: int, seed: int) -> list[dict[str, list[str]]]:
    """生成实体池互斥的马来西亚合成语料；规则标注后仍需人工抽查。"""
    rng = random.Random(seed)
    pool = MALAYSIAN_POOLS[split]
    local_templates = [template for template in TEMPLATES if "{PER2}" not in template]
    rows = []
    for index in range(size):
        if index % 8 == 0:
            neutral = {
                "train": "The submitted form contains no named entity .",
                "validation": "This local validation sentence has no entity .",
                "test": "This local test sentence has no entity .",
            }[split]
            rows.append(_annotate(neutral, {}))
            continue
        template = rng.choice(local_templates)
        values = {kind: rng.choice(items) for kind, items in pool.items() if "{" + kind + "}" in template}
        rows.append(_annotate(template.format(**values), values))
    rng.shuffle(rows)
    return rows


def _write_jsonl(rows: list[dict], path: Path) -> None:
    """将样本保存为一行一个 JSON 对象的 UTF-8 JSONL。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    """生成三个 Split；发现规范化句子跨 Split 重复时立即失败。"""
    # 完整句子和实体字符串都必须跨 split 隔离，避免验证/测试指标因记忆
    # 训练集专有名词而虚高。
    for entity_type in ("PER", "LOC", "ORG"):
        split_sets = {split: set(values[entity_type]) for split, values in ENTITY_POOLS.items()}
        for left, right in (("train", "validation"), ("train", "test"), ("validation", "test")):
            overlap = split_sets[left] & split_sets[right]
            if overlap:
                raise RuntimeError(f"{entity_type} entity leakage between {left}/{right}: {sorted(overlap)}")

    sizes = {"train": 2400, "validation": 300, "test": 300}
    all_texts: set[str] = set()
    summary = {}
    for offset, (split, size) in enumerate(sizes.items()):
        rows = generate_split(split, size, SEED + offset)
        texts = {row["text"].lower() for row in rows}
        overlap = all_texts & texts
        if overlap:
            # 绝不自动忽略泄漏；失败能迫使开发者先修复数据再训练。
            raise RuntimeError(f"Sentence leakage into {split}: {sorted(overlap)[:3]}")
        all_texts |= texts
        _write_jsonl(rows, PROCESSED_DIR / f"{split}.jsonl")
        summary[split] = {"rows": len(rows), "unique_sentences": len(texts)}

    challenge_texts = [
        "Farah works at Telekom Malaysia in Cyberjaya.",
        "Kumar studies at Universiti Sains Malaysia in George Town.",
        "Aina met Jason at Hospital Kuala Lumpur.",
        "The weather is beautiful today.",
    ]
    MALAYSIAN_DIR.mkdir(parents=True, exist_ok=True)
    (MALAYSIAN_DIR / "challenge.txt").write_text("\n".join(challenge_texts) + "\n", encoding="utf-8")
    local_sizes = {"train": 160, "validation": 40, "test": 60}
    local_texts: set[str] = set()
    for offset, (split, size) in enumerate(local_sizes.items()):
        rows = generate_malaysian_split(split, size, SEED + 100 + offset)
        texts = {row["text"].lower() for row in rows}
        if local_texts & texts:
            raise RuntimeError(f"Malaysian sentence leakage into {split}")
        local_texts |= texts
        _write_jsonl(rows, MALAYSIAN_DIR / f"{split}.jsonl")
        summary[f"malaysian_{split}"] = {"rows": len(rows), "unique_sentences": len(texts)}
    (PROCESSED_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

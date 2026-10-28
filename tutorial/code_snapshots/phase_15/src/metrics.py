"""按实体边界与类型完全匹配计算 Entity-level Precision/Recall/F1。"""

from __future__ import annotations

from collections import defaultdict


def bio_to_spans(labels: list[str]) -> set[tuple[int, int, str]]:
    """把 BIO 序列转换为 (start, end_exclusive, entity_type) 集合。"""
    spans: set[tuple[int, int, str]] = set()
    start: int | None = None
    current_type: str | None = None
    for index, label in enumerate(labels + ["O"]):
        if label.startswith("B-") or label == "O" or (label.startswith("I-") and label[2:] != current_type):
            if start is not None and current_type is not None:
                spans.add((start, index, current_type))
            if label.startswith("B-"):
                start, current_type = index, label[2:]
            else:
                start, current_type = None, None
    return spans


def entity_metrics(gold_sequences: list[list[str]], predicted_sequences: list[list[str]]) -> dict:
    """累计 PER/LOC/ORG 的 TP、FP、FN，并计算各类与总体指标。"""
    counts = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    for gold, predicted in zip(gold_sequences, predicted_sequences, strict=True):
        gold_spans = bio_to_spans(gold)
        predicted_spans = bio_to_spans(predicted)
        for entity_type in {"PER", "LOC", "ORG"}:
            gold_type = {span for span in gold_spans if span[2] == entity_type}
            pred_type = {span for span in predicted_spans if span[2] == entity_type}
            counts[entity_type]["tp"] += len(gold_type & pred_type)
            counts[entity_type]["fp"] += len(pred_type - gold_type)
            counts[entity_type]["fn"] += len(gold_type - pred_type)

    def calculate(item: dict[str, int]) -> dict[str, float | int]:
        # 分母为 0 时返回 0，避免空实体数据导致 ZeroDivisionError。
        tp, fp, fn = item["tp"], item["fp"], item["fn"]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return {**item, "precision": precision, "recall": recall, "f1": f1}

    result = {entity_type: calculate(counts[entity_type]) for entity_type in ("PER", "LOC", "ORG")}
    total = {key: sum(counts[kind][key] for kind in counts) for key in ("tp", "fp", "fn")}
    result["overall"] = calculate(total)
    return result

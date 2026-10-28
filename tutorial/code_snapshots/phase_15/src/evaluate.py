"""在独立 Test Set 上评估冻结 checkpoint，并保存真实 Entity-level 指标。"""

from __future__ import annotations

import json

from .constants import MALAYSIAN_DIR, MODELS_DIR, PROCESSED_DIR, REPORTS_DIR
from .dataset import load_jsonl
from .metrics import entity_metrics
from .predict import Predictor
from .preprocessing import save_json


def main() -> None:
    """评估入口；此文件不创建 Optimizer，也不会修改模型权重。"""
    predictor = Predictor(MODELS_DIR / "best_model.pt")
    rows = load_jsonl(PROCESSED_DIR / "test.jsonl")
    gold = [row["labels"] for row in rows]
    predicted = [predictor.predict_tokens(row["tokens"]) for row in rows]
    metrics = entity_metrics(gold, predicted)
    report = {"dataset": "synthetic leakage-safe test split", "sentences": len(rows), "metrics": metrics}
    save_json(report, REPORTS_DIR / "test_metrics.json")
    print(json.dumps(report, indent=2))
    local_rows = load_jsonl(MALAYSIAN_DIR / "test.jsonl")
    local_metrics = entity_metrics(
        [row["labels"] for row in local_rows],
        [predictor.predict_tokens(row["tokens"]) for row in local_rows],
    )
    local_report = {"dataset": "synthetic Malaysian local test split", "sentences": len(local_rows), "metrics": local_metrics}
    save_json(local_report, REPORTS_DIR / "malaysian_test_metrics.json")
    print(json.dumps(local_report, indent=2))


if __name__ == "__main__":
    main()

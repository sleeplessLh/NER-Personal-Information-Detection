"""运行固定的真实英文挑战矩阵，保存成功与失败，不用它训练或选模。"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.predict import Predictor
from src.redact import redact_text

CASES = [
    ("PERSON-US", "Barack Obama spoke yesterday.", [("Barack Obama", "PER")]),
    ("PERSON-Indian", "Priyanka Chopra arrived early.", [("Priyanka Chopra", "PER")]),
    ("PERSON-Chinese", "Li Wei submitted the report.", [("Li Wei", "PER")]),
    ("LOCATION", "The conference took place in Toronto.", [("Toronto", "LOC")]),
    ("ORG-university", "Stanford University opened a laboratory.", [("Stanford University", "ORG")]),
    ("ORG-hospital", "Johns Hopkins Hospital hired a specialist.", [("Johns Hopkins Hospital", "ORG")]),
    ("MIXED", "Aisha Rahman joined Google in Singapore.", [("Aisha Rahman", "PER"), ("Google", "ORG"), ("Singapore", "LOC")]),
    ("NO-ENTITY", "The weather is beautiful and the room is quiet.", []),
    ("MALAYSIAN", "Nurul Izzah met Petronas executives in Putrajaya.", [("Nurul Izzah", "PER"), ("Petronas", "ORG"), ("Putrajaya", "LOC")]),
    ("REPEATED", "Sarah met Sarah at Microsoft in London.", [("Sarah", "PER"), ("Sarah", "PER"), ("Microsoft", "ORG"), ("London", "LOC")]),
    ("MULTI-SENTENCE", "John works at Apple in New York. Sarah studies at Oxford University in London.", [("John", "PER"), ("Apple", "ORG"), ("New York", "LOC"), ("Sarah", "PER"), ("Oxford University", "ORG"), ("London", "LOC")]),
    ("PUNCTUATION", "(John Carter), from Microsoft, visited London!", [("John Carter", "PER"), ("Microsoft", "ORG"), ("London", "LOC")]),
    ("UNKNOWN-WORDS", "Xylophonia Zqv works for Quasarion Labs in Vexford.", [("Xylophonia Zqv", "PER"), ("Quasarion Labs", "ORG"), ("Vexford", "LOC")]),
]


def main() -> None:
    predictor = Predictor()
    results = []
    for name, text, expected in CASES:
        prediction = predictor.predict(text)
        actual = [(entity["text"], entity["type"]) for entity in prediction["entities"]]
        offsets_ok = all(text[e["start"] : e["end"]] == e["text"] for e in prediction["entities"])
        results.append({
            "name": name,
            "text": text,
            "expected": expected,
            "actual": actual,
            "offsets_ok": offsets_ok,
            "redacted": redact_text(text, prediction["entities"]),
            "passed": actual == expected and offsets_ok,
        })
    payload = {
        "purpose": "manual robustness evidence only; never used for training or model selection",
        "passed": sum(row["passed"] for row in results),
        "total": len(results),
        "results": results,
    }
    output = ROOT / "reports" / "manual_acceptance.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"passed": payload["passed"], "total": payload["total"]}, indent=2))


if __name__ == "__main__":
    main()

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
    ("MALAYSIAN-STUDENT", "Ahmad Ali, a student from Universiti Teknologi Malaysia, attended an event in Johor Bahru.", [("Ahmad Ali", "PER"), ("Universiti Teknologi Malaysia", "ORG"), ("Johor Bahru", "LOC")]),
    ("STUDENT-COMPLAINT", "Nur Aisyah submitted a complaint to Taylor University in Subang Jaya.", [("Nur Aisyah", "PER"), ("Taylor University", "ORG"), ("Subang Jaya", "LOC")]),
    ("INTERNATIONAL-STUDENT", "Li Wei studies at Stanford University in Toronto.", [("Li Wei", "PER"), ("Stanford University", "ORG"), ("Toronto", "LOC")]),
    ("SCHOOL-INCIDENT", "Siti Hajar reported an incident at Victoria Secondary School in Kuala Lumpur.", [("Siti Hajar", "PER"), ("Victoria Secondary School", "ORG"), ("Kuala Lumpur", "LOC")]),
    ("SUPPORT-CHAT", "The student support team contacted Arjun Nair at Monash University.", [("Arjun Nair", "PER"), ("Monash University", "ORG")]),
    ("STUDENT-FEEDBACK", "Priyanka Chopra submitted feedback about a course at Sunway College.", [("Priyanka Chopra", "PER"), ("Sunway College", "ORG")]),
    ("STUDENT-ACTIVITY", "Daniel Wong attended a student activity in Putrajaya.", [("Daniel Wong", "PER"), ("Putrajaya", "LOC")]),
    ("ADMIN-REPORT", "The university report says Mei Lin lives in George Town.", [("Mei Lin", "PER"), ("George Town", "LOC")]),
    ("REPEATED-STUDENT", "Sarah met Sarah at New York University in New York.", [("Sarah", "PER"), ("Sarah", "PER"), ("New York University", "ORG"), ("New York", "LOC")]),
    ("MULTI-SENTENCE", "John studies at Oxford University in London. Aisha Rahman requested support from Universiti Malaya.", [("John", "PER"), ("Oxford University", "ORG"), ("London", "LOC"), ("Aisha Rahman", "PER"), ("Universiti Malaya", "ORG")]),
    ("PUNCTUATION", "(John Carter), a student at Oxford University, visited London!", [("John Carter", "PER"), ("Oxford University", "ORG"), ("London", "LOC")]),
    ("NO-ENTITY", "The assignment deadline is next week and the classroom is quiet.", []),
    ("UNKNOWN-STUDENT", "Xylophonia Zqv studies at Quasarion University in Vexford.", [("Xylophonia Zqv", "PER"), ("Quasarion University", "ORG"), ("Vexford", "LOC")]),
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
        "purpose": "student-privacy robustness evidence only; never used for training or model selection",
        "passed": sum(row["passed"] for row in results),
        "total": len(results),
        "results": results,
    }
    output = ROOT / "reports" / "manual_acceptance.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"passed": payload["passed"], "total": payload["total"]}, indent=2))


if __name__ == "__main__":
    main()

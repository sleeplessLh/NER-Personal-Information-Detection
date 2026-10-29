"""静态验证 30 天计划、Phase 清单、面试材料与页码映射。"""

from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "NER_30_Day_Learning_Plan.md"
CHECKLIST = ROOT / "PHASE_LEARNING_CHECKLIST.md"
INTERVIEW = ROOT / "INTERVIEW_PREPARATION.md"
MAIN_PDF = ROOT / "output/pdf/NER_From_Zero_To_Complete_Project_CN.pdf"
PLAN_PDF = ROOT / "output/pdf/NER_30_Day_Learning_Plan.pdf"

EXPECTED_START = {
    0: 9, 1: 13, 2: 25, 3: 29, 4: 30, 5: 35, 6: 42, 7: 47,
    8: 53, 9: 56, 10: 71, 11: 74, 12: 79, 13: 82, 14: 86,
    15: 94, 16: 98, 17: 101, 18: 104, 19: 110, 20: 121, 21: 132,
}


def main() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    interview = INTERVIEW.read_text(encoding="utf-8")

    days = [int(value) for value in re.findall(r"^## Day (\d{2})", plan, re.MULTILINE)]
    assert days == list(range(1, 31)), days
    for field in ["知识点：", "创建或修改：", "跟敲代码：", "运行命令：", "预期输出：", "完成判断：", "失败检查：", "预计时间："]:
        assert plan.count(field) == 30, (field, plan.count(field))

    phases = [int(value) for value in re.findall(r"^## Phase (\d{2})", checklist, re.MULTILINE)]
    assert phases == list(range(22)), phases
    for field in ["Knowledge Check", "Coding Check", "Execution Check", "Expected Result", "Common Errors", "Completion Criteria", "Function Contracts and File Relationships"]:
        assert checklist.count(f"### {field}") == 22, field

    questions = re.findall(r"^## (\d+)\. ", interview, re.MULTILINE)
    assert len(questions) == 15, len(questions)
    for text in (plan, checklist, interview):
        assert "Independent Human Learning Test: NOT VERIFIED" in text

    main_reader = PdfReader(MAIN_PDF)
    assert len(main_reader.pages) == 141
    page_text = [page.extract_text() or "" for page in main_reader.pages]
    for phase, page in EXPECTED_START.items():
        assert f"Phase {phase:02d}" in page_text[page - 1], (phase, page)

    plan_reader = PdfReader(PLAN_PDF)
    joined = "\n".join(page.extract_text() or "" for page in plan_reader.pages)
    for day in range(1, 31):
        assert f"Day {day:02d}" in joined, day
    assert "NOT VERIFIED" in joined
    assert all((ROOT / path).exists() for path in [
        "src/train.py", "src/evaluate.py", "src/predict.py", "src/redact.py",
        "app/main.py", "tests/test_api.py", "scripts/student_reproduction_audit.py",
    ])

    print(f"LEARNING MATERIAL VALIDATION PASSED: {len(days)} days, {len(phases)} phases, {len(questions)} interview questions, {len(plan_reader.pages)} PDF pages")


if __name__ == "__main__":
    main()

"""对 A-Z 教材执行结构、内容密度和可操作性检查。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "tutorial"
MANIFEST = json.loads((TUTORIAL / "manifest.json").read_text(encoding="utf-8"))

FORBIDDEN_PLACEHOLDERS = ("TO" + "DO", "TBD", "待补充", "自行实现", "Update accordingly")
OPERATION_WORDS = ("打开", "创建", "找到", "输入", "运行", "点击", "PowerShell", "VS Code")
TEST_WORDS = ("pytest", "实际输出", "PASS", "通过", "assert")


def validate_phase(phase: dict) -> list[str]:
    path = TUTORIAL / "chapters" / f"phase_{phase['id']}.md"
    if not path.exists():
        return [f"missing chapter: {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if len(text) < 3500:
        errors.append(f"{path.name}: too short ({len(text)} chars; minimum 3500)")
    for heading in MANIFEST["required_sections"]:
        if heading not in text:
            errors.append(f"{path.name}: missing section `{heading}`")
    if "```" not in text:
        errors.append(f"{path.name}: no executable code/command block")
    if not re.search(r"(?:src|app|tests|learning|tutorial)/[\w./-]+", text):
        errors.append(f"{path.name}: no explicit project file path")
    if not any(word in text for word in OPERATION_WORDS):
        errors.append(f"{path.name}: no concrete IDE/terminal operation")
    if not any(word in text for word in TEST_WORDS):
        errors.append(f"{path.name}: no concrete validation evidence")
    for placeholder in FORBIDDEN_PLACEHOLDERS:
        if placeholder in text:
            errors.append(f"{path.name}: forbidden placeholder `{placeholder}`")
    lesson_count = len(re.findall(r"^###\s+\d+\.\s+Lesson|^####\s+Lesson", text, flags=re.MULTILINE))
    if lesson_count < 3:
        errors.append(f"{path.name}: fewer than 3 incremental lessons")
    if phase["id"] == "09":
        for lesson in range(1, 21):
            if not re.search(rf"Lesson\s+{lesson}\b", text):
                errors.append(f"{path.name}: missing mandatory neural-network Lesson {lesson}")
        if len(text) < 18000:
            errors.append(f"{path.name}: neural-network chapter too short")
    return errors


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    errors = [error for phase in MANIFEST["phases"] for error in validate_phase(phase)]
    if errors:
        print("TUTORIAL VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"TUTORIAL VALIDATION PASSED: {len(MANIFEST['phases'])} phases")


if __name__ == "__main__":
    main()

"""检查教材路径、阶段快照和最终正式源码的一致性。"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "tutorial"
MANIFEST = json.loads((TUTORIAL / "manifest.json").read_text(encoding="utf-8"))
FINAL_SOURCE = [
    "pyproject.toml", "src/constants.py", "src/preprocessing.py", "src/generate_data.py",
    "src/dataset.py", "src/model.py", "src/metrics.py", "src/train.py", "src/evaluate.py",
    "src/predict.py", "src/redact.py", "app/main.py",
]


def digest(path: Path) -> str:
    # Git on Windows may check out text as CRLF even when the verified snapshot
    # was created with LF.  Normalize line endings so this content check remains
    # portable and does not report a false mismatch after a fresh clone.
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    errors: list[str] = []
    referenced_paths: set[str] = set()
    for phase in MANIFEST["phases"]:
        chapter = TUTORIAL / "chapters" / f"phase_{phase['id']}.md"
        if not chapter.exists():
            errors.append(f"missing chapter {chapter.relative_to(ROOT)}")
            continue
        text = chapter.read_text(encoding="utf-8")
        referenced_paths.update(re.findall(r"`((?:src|app|tests|learning|tutorial)/[\w./-]+)`", text))
        snapshot = TUTORIAL / "code_snapshots" / f"phase_{phase['id']}" / "snapshot.json"
        if not snapshot.exists():
            errors.append(f"missing snapshot manifest for phase {phase['id']}")
    for relative in sorted(referenced_paths):
        if not (ROOT / relative).exists() and not any(
            (TUTORIAL / "code_snapshots" / f"phase_{phase['id']}" / relative).exists()
            for phase in MANIFEST["phases"]
        ):
            errors.append(f"unresolved tutorial path: {relative}")
    final_manifest = TUTORIAL / "code_snapshots" / "phase_21" / "snapshot.json"
    if final_manifest.exists():
        data = json.loads(final_manifest.read_text(encoding="utf-8"))
        for relative in FINAL_SOURCE:
            official = ROOT / relative
            expected = data.get("files", {}).get(relative)
            if not official.exists():
                errors.append(f"missing official final file: {relative}")
            elif expected != digest(official):
                errors.append(f"final snapshot mismatch: {relative}")
    if errors:
        print("TUTORIAL SYNCHRONIZATION FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"TUTORIAL SYNCHRONIZATION PASSED: {len(referenced_paths)} referenced paths")


if __name__ == "__main__":
    main()

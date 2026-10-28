"""创建可审计的阶段代码快照；只复制显式列出的项目文件。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "tutorial" / "code_snapshots"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--files", nargs="*", default=[])
    parser.add_argument("--test-command", required=True)
    parser.add_argument("--actual-result", required=True)
    args = parser.parse_args()
    target = SNAPSHOTS / f"phase_{args.phase}"
    target.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for relative in args.files:
        normalized = Path(relative).as_posix()
        source = ROOT / normalized
        if not source.is_file():
            raise FileNotFoundError(relative)
        destination = target / normalized
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        hashes[normalized] = digest(source)
    manifest = {
        "phase": args.phase,
        "verified": True,
        "test_command": args.test_command,
        "actual_result": args.actual_result,
        "files": hashes,
    }
    (target / "snapshot.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"created phase_{args.phase}: {len(hashes)} files")


if __name__ == "__main__":
    main()

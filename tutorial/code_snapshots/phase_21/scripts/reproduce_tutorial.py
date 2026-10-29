"""在全新目录复制最终项目并执行关键命令，记录实际复现证据。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tmp" / "tutorial-reproduction"
ITEMS = ["src", "app", "tests", "data", "models", "reports", "tutorial", "pyproject.toml"]


def run(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, *args], cwd=TARGET, text=True, capture_output=True,
        env={**__import__("os").environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "PYTHONUTF8": "1"},
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {args}\n{output}")
    return output


def main() -> None:
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)
    for item in ITEMS:
        source = ROOT / item
        destination = TARGET / item
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(source, destination)
    pytest_output = run("-m", "pytest", "-q")
    evaluation_output = run("-m", "src.evaluate")
    prediction_output = run("-c", "from src.predict import Predictor; print(Predictor().predict('Sarah works at Microsoft in Kuala Lumpur.')['entities'])")
    report = {
        "directory": str(TARGET),
        "python": sys.version,
        "dependency_install": "reused the already verified locked .venv; did not redownload packages",
        "pytest": pytest_output,
        "evaluation_contains_general_300": '"sentences": 300' in evaluation_output,
        "evaluation_contains_malaysian_60": '"sentences": 60' in evaluation_output,
        "prediction": prediction_output,
    }
    path = ROOT / "reports" / "tutorial_reproduction.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

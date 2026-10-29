"""按 PDF 的阶段文件清单累积构建新目录，并逐阶段执行 checkpoint。

此脚本只用于审计：copy2 等价于学生从 PDF 的“完整可复制文件”逐字输入，
不会一次复制整个项目，也不会复制开发目录的 checkpoint、data 或 reports。
环境安装、真实浏览器点击和概念口述仍需单独人工验收。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tutorial.build_pdf import PHASE_FILES

TARGET = ROOT / "tmp" / "NER_Tutorial_Reproduction_Test_2"
REPORT = ROOT / "reports" / "student_phase_reproduction.json"


def run(command: list[str], cwd: Path = TARGET) -> dict[str, object]:
    environment = os.environ.copy()
    environment["OMP_NUM_THREADS"] = "1"
    environment["MKL_NUM_THREADS"] = "1"
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
        check=False,
    )
    return {
        "command": subprocess.list2cmdline(command),
        "exit_code": completed.returncode,
        "output": completed.stdout[-4000:],
    }


def copy_phase_files(phase: str) -> list[str]:
    copied: list[str] = []
    for relative in PHASE_FILES[phase]:
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(f"Phase {phase} tutorial file missing: {relative}")
        destination = TARGET / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(relative)
    return copied


def checkpoints(python: str) -> dict[str, list[str]]:
    return {
        "00": [python, "-c", "from pathlib import Path; assert Path('README.md').is_file()"],
        "01": [python, "learning/hello_python.py"],
        "02": [python, "learning/python_foundations.py"],
        "03": [python, "learning/bio_demo.py"],
        "04": [python, "-c", "from src.constants import LABELS; assert len(LABELS)==8; print(LABELS)"],
        "05": [python, "-m", "src.generate_data"],
        "06": [python, "-m", "pytest", "tests/test_preprocessing.py", "-q"],
        "07": [python, "-m", "learning.tensor_demo"],
        "08": [python, "-m", "learning.dataloader_demo"],
        "09": [python, "-m", "pytest", "tests/test_model_versions.py", "-q"],
        "10": [python, "-m", "learning.training_step_demo"],
        "11": [python, "-m", "src.train", "--epochs", "16", "--batch-size", "64", "--learning-rate", "0.003"],
        "12": [python, "-c", "from src.predict import Predictor; print(Predictor().predict('Li Wei visited Toronto.')['entities'])"],
        "13": [python, "-m", "pytest", "tests/test_redaction.py", "-q"],
        "14": [python, "-c", "import torch; c=torch.load('models/best_model.pt',weights_only=False); print(c['dataset_counts']); assert c['dataset_counts']['malaysian_training']==160"],
        "15": [python, "-m", "src.evaluate"],
        "16": [python, "-m", "pytest", "tests/test_text_api.py", "-q"],
        "17": [python, "-m", "pytest", "tests/test_file_api.py", "-q"],
        "18": [python, "-m", "pytest", "tests/test_web_ui.py", "-q"],
        "19": [python, "-m", "pytest", "-q"],
        "20": [python, "-c", "from pathlib import Path; assert all(Path(x).is_file() for x in ['README.md','MODEL_ACCEPTANCE_REPORT.md','PRESENTATION_MATERIALS.md'])"],
        "21": [python, "-m", "pytest", "-q"],
    }


def main() -> None:
    if TARGET.exists():
        resolved = TARGET.resolve()
        expected_parent = (ROOT / "tmp").resolve()
        if resolved.parent != expected_parent or resolved.name != "NER_Tutorial_Reproduction_Test_2":
            raise RuntimeError(f"Refusing to replace unexpected path: {resolved}")
        shutil.rmtree(resolved)
    TARGET.mkdir(parents=True)
    results: list[dict[str, object]] = []
    phase_commands = checkpoints(sys.executable)
    for phase in [f"{number:02d}" for number in range(22)]:
        copied = copy_phase_files(phase)
        evidence = run(phase_commands[phase])
        item = {"phase": phase, "copied_from_tutorial": copied, **evidence}
        results.append(item)
        print(f"Phase {phase}: {'PASS' if evidence['exit_code'] == 0 else 'FAIL'}")
        if evidence["exit_code"] != 0:
            break
    payload = {
        "target": str(TARGET),
        "method": "phase-by-phase tutorial file transcription equivalence; no final project bulk copy",
        "environment": sys.version,
        "results": results,
        "passed": sum(item["exit_code"] == 0 for item in results),
        "total_required": 22,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if payload["passed"] != 22:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

# Phase 04：创建项目骨架、配置与 Git

## 1. 本阶段学习目标

把前三阶段的练习目录升级为正式 Python 项目：理解 package、module、relative import、path、configuration、random seed，并创建 `src/constants.py`、`src/__init__.py`、`tests/`、`data/`、`models/`、`reports/` 与 `.gitignore`。结束时 constants 可从任意工作目录 import，路径仍指向项目根目录。

## 2. 本阶段需要掌握的知识

文件夹与 Python package 的差别；`__init__.py`；绝对/相对路径；`Path(__file__)`；constant；seed；Git repository、working tree、ignore；为什么 `.venv`、cache 与临时 QA 文件不应提交。

## 3. 从零解释知识点

Module 是一个 `.py` 文件；package 是可 import 的模块目录。`src/__init__.py` 即使为空，也明确告诉读者这是 package。`__file__` 是当前文件实际路径；`Path(__file__).resolve().parents[1]` 从 `src/constants.py` 向上得到项目根目录，因此不依赖 PowerShell 当前在哪。

Constant 是约定不在运行中修改的配置，使用大写命名。LABELS 顺序会写入 checkpoint；一旦训练后改变顺序，旧权重输出 ID 会被错误解释。SEED 让随机步骤尽量可复现，但不同硬件/库仍可能有轻微差异。

Git 记录源代码演化；`.gitignore` 只排除不该跟踪的路径，不会删除文件。当前仓库没有 commit，所以教材快照明确是本轮重建历史。

## 4. 本阶段开始前的项目状态

```text
learning/                       [已有]
tutorial/chapters/phase_00-03  [已有]
src/                            [本阶段正式启用]
  __init__.py                   [新增]
  constants.py                  [新增]
tests/                          [新增]
data/raw/                       [新增]
models/ reports/               [新增]
.gitignore pyproject.toml       [创建或检查]
```

## 5. 本阶段需要使用的工具

VS Code Explorer 创建目录/文件；Integrated PowerShell 位于根目录；Git 用只读 `status` 检查。先执行 `Get-Location`，再执行 `git status -sb`。若 Git 报 dubious ownership，只在本仓库命令上使用 `git -c safe.directory='D:/AIROST/Intern-MachineLearning' status -sb`，不要全局信任陌生路径。

### 6. Lesson 04.1：创建 package 与目录

在 Explorer 新建 `src`，其中新建空 `__init__.py`。再创建 `tests`、`data/raw`、`models`、`reports`。PowerShell 等价命令：

```powershell
New-Item -ItemType Directory -Force src,tests,data\raw,models,reports
New-Item -ItemType File -Force src\__init__.py
```

`-Force` 允许目录已存在，不代表删除内容。完成后运行 `python -c "import src; print(src.__name__)"`，预期 `src`。

### 7. Lesson 04.2：逐行创建 constants

打开 `src/constants.py`，第一行：

```python
from pathlib import Path
```

接着输入：

```python
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MALAYSIAN_DIR = DATA_DIR / "malaysian"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
```

Path 的 `/` 是路径拼接，不是数学除法。返回值仍是 Path。然后定义：

```python
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"
LABELS = ["<PAD>", "O", "B-PER", "I-PER", "B-LOC", "I-LOC", "B-ORG", "I-ORG"]
SEED = 42
```

PAD label 只用于 batch 补齐，不是数据集真实标签。UNK 代表词表未见 token。

### 8. Lesson 04.3：建立 `.gitignore` 与依赖入口

`.gitignore` 至少包含：

```text
.venv/
__pycache__/
.pytest_cache/
.pytest-tmp/
*.pyc
```

不要忽略 `src/`、`tests/`、教程章节或小型 checkpoint。`pyproject.toml` 声明 Python 3.11-3.12 与依赖；`uv.lock` 锁具体解析结果。学生此时不需要手写全部 lock file，执行 `uv sync --all-groups` 由工具处理。

### 9. Lesson 04.4：从不同目录验证路径

根目录运行：

```powershell
python -c "from src.constants import ROOT,LABELS; print(ROOT); print(len(LABELS))"
```

预期根路径与数字 8。再 `Set-Location tests`，使用 `python -c "import sys; sys.path.insert(0,'..'); from src.constants import ROOT; print(ROOT)"`，路径仍相同，随后 `Set-Location ..` 返回。实际正式测试通过 import constants。

## 10. 完整代码回顾

阶段结束的 `src/constants.py` 应只包含路径、特殊 token、labels 和 seed，不 import torch，也不执行业务逻辑。打开真实文件逐行核对；`python -m py_compile src\constants.py` 应无输出并退出 0。

## 11. 跨文件调用关系

未来 `generate_data` 读取数据目录；`train/evaluate/predict` 读取 models/reports；Dataset/metrics 使用 LABELS。所有文件 import constants，constants 不反向 import 它们，避免 circular import。

## 12. 数据流解释

本阶段没有训练数据流。配置流是 `constants.py` Path/list/int -> 其他 modules import -> 创建/读取统一位置。LABELS list 的 index 以后成为 label ID。

## 13. 常见错误

`parents[0]` 得到 src 而非 root；在字符串中手写反斜线可能出现转义；把 PAD 当 gold label；训练后重排 LABELS；误提交 `.venv`；在错误目录运行 Git。逐项用 print、status 和测试定位。

## 14. Checkpoint

```powershell
python -m py_compile src\constants.py
python -c "from src.constants import ROOT,LABELS,PAD_TOKEN; assert ROOT.name=='Intern-MachineLearning'; assert len(LABELS)==8; assert PAD_TOKEN=='<PAD>'; print('PASS')"
git -c safe.directory='D:/AIROST/Intern-MachineLearning' status -sb
```

真实验收：constants import 与三项断言 PASS。Git 当前显示未提交文件是事实，不宣称已有公开仓库。

## 15. 学生练习

打印每个 label 与 index；解释为什么 PAD 是 0；新增 `DATA_DIR` 后验证类型是 Path；用错误 parent 创建临时变量观察差异；检查 `.gitignore` 是否忽略 `.venv`。

## 16. 面试准备

"I centralize stable paths, labels and the random seed in one dependency-free module. Paths are derived from `__file__`, so commands do not depend on the current directory. Label order is checkpoint metadata and must remain stable."

## 17. 下一阶段预告

Phase 05 使用 constants 中的数据目录创建一般与 Malaysian JSONL，并在写文件前验证 BIO、实体池隔离和跨 split 完整句泄漏。

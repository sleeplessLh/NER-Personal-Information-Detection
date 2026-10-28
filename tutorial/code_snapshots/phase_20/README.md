# Personal Information Detection in Text (NER)

## Project Introduction

这是一个从随机权重开始、真实训练的英文 NER 教学项目。核心为 PyTorch `Embedding + casing features + BiLSTM + Linear`，识别 `PER`、`LOC`、`ORG`，返回原始字符位置并生成脱敏文本。它不调用 OpenAI/Gemini/Cloud NER，也不加载 spaCy 或 Hugging Face 现成 NER pipeline。

## Installation - Windows 11 / PowerShell

需要 Python 3.11-3.12、Git、VS Code 与 [uv](https://docs.astral.sh/uv/)。

```powershell
git clone <your-public-repository-url>
cd Intern-MachineLearning
uv sync --all-groups
uv run python -c "import torch; print(torch.__version__)"
```

仓库目前尚未发布；创建公开 GitHub repository 后替换占位 URL。

## Dependencies

运行依赖锁定在 `pyproject.toml`/`uv.lock`：PyTorch、NumPy、pandas、scikit-learn、FastAPI、Uvicorn、Pydantic、Jinja2、pypdf、python-multipart。开发依赖包括 pytest、pytest-cov、httpx、ReportLab、pdfplumber。

## Dataset

本版本使用可重现的合成英文 BIO 语料，不声称是 CoNLL-2003。一般数据为 2,400 train / 300 validation / 300 test；马来西亚本地合成数据为 160 / 40 / 60。完整句子与实体池跨 split 隔离，但句法模板共享，因此测试明显比真实文本简单。

标签：`O, B/I-PER, B/I-LOC, B/I-ORG`；没有 `MISC`。本地数据包含合成人名以及马来西亚城市、大学、公司、医院和政府机构名称。它不是现实用户数据。

```powershell
uv run python -m src.generate_data
```

## Model Architecture

`token IDs -> trainable Embedding(64)` 与 `4 casing features -> Linear(8)` 拼接，然后进入一层双向 LSTM（每方向 96），Dropout 0.25，最后 Linear 输出 8 个标签 logits。模型共有 143,536 参数。

没有使用 CRF：这是题目允许的 BiLSTM Token Classifier 备选，便于 CPU 与零基础复现；缺点是无法联合学习 BIO 转移，非法初始 I-tag 由抽取器安全修复。

## Training Instructions

```powershell
uv run python -m src.generate_data
uv run python -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003
uv run python -m src.evaluate
```

训练集会明确合入 Malaysian train，validation 合入 Malaysian validation；两个 test split 不参与训练或选模。checkpoint 保存权重、vocabulary、labels、config、seed、数据计数、最佳 epoch。

## Running Instructions

```powershell
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
uv run python -m uvicorn app.main:app --reload
```

打开 `http://127.0.0.1:8000`。网页支持文本和 `.txt`/`.pdf` 文件。文件上限 5 MB；TXT 必须 UTF-8；PDF 必须有文字层；扫描件不支持 OCR。

API：`POST /api/predict` JSON 为 `{"text":"Sarah works at Microsoft in Kuala Lumpur."}`。结果含 token、BIO tag、实体文字/类型、token span、半开字符区间 `start/end` 与 `redacted_text`。

## Testing Instructions

```powershell
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
uv run python -m pytest -q --cov=src --cov=app --cov-report=term-missing
```

最终实测：核心工程验收 22 项全部保留；加入 6 项教学模型演进测试后，完整套件为 `28 passed in 3.52s`（空目录教程复现环境）。另以独立 Uvicorn 进程完成真实 HTTP POST 验收。

## Evaluation Results

- CPU training loop: 8 epochs，6.9201 seconds
- Best epoch: 7
- Validation entity-level F1: 0.9986
- General synthetic test: P/R/F1 = 1.0000/1.0000/1.0000
- Malaysian synthetic test: P/R/F1 = 1.0000/1.0000/1.0000
- Person recall: 1.0000 on both synthetic test splits

分数只适用于共享模板的合成分布。手动挑战句 `Dr. Evelyn Carter ... Oxford` 漏掉姓名并误标机构，证明模型尚未具备真实泛化能力。

## Project Structure

```text
app/main.py                 FastAPI、网页、上传、文件限制
src/generate_data.py        一般与 Malaysian 数据生成/泄漏检查
src/preprocessing.py        Token、字符 span、BIO、vocabulary
src/dataset.py              Dataset、padding、mask、word dropout
src/model.py                自定义 BiLSTM token classifier
src/train.py                训练/验证/保存 checkpoint
src/evaluate.py             一般与 Malaysian 独立 test
src/predict.py              CPU checkpoint 推理/实体抽取
src/redact.py               字符 span 原样脱敏
tests/                      22 项核心工程验收 + 6 项教学模型演进测试
models/best_model.pt        最终训练 checkpoint
reports/                    JSON 训练与评估证据
MODEL_ACCEPTANCE_REPORT.md  需求、软件、ML、HTTP、手测报告
PRESENTATION_MATERIALS.md   英文演示稿与面试问答
output/pdf/                 最终中文教程
```

## Limitations

- 合成模板语料不等于真实 incident report、support chat 或 CoNLL-2003。
- PER/LOC/ORG 不覆盖电话、邮箱、Student ID、Passport、完整地址等 PII。
- 无 CRF；无 OCR；仅英文正则分词。
- 高风险大学、医院或企业流程必须由人工复核，不能直接自动发布脱敏结果。
- 公开 GitHub 发布尚未执行，因为当前没有用户仓库授权。

详细证据见 `MODEL_ACCEPTANCE_REPORT.md`；完整学习路径见 `output/pdf/NER_From_Zero_To_Complete_Project_CN.pdf`。

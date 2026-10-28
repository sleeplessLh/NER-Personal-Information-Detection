# Personal Information Detection in Text (NER)

## Project Overview

这是一个从随机权重开始训练的英文命名实体识别（NER）项目。核心预测器由 PyTorch 自定义 `Embedding + casing features + BiLSTM + Linear` 实现，识别 `PERSON (PER)`、`LOCATION (LOC)`、`ORGANISATION (ORG)`，返回字符位置并生成脱敏文本。

项目不调用外部 AI/NER API，也不加载 spaCy/Hugging Face 现成 NER pipeline。仓库直接包含经过训练的 `models/best_model.pt`，Clone 后不需要重新训练即可预测。

## Competition Requirements

| Requirement | Status |
|---|---|
| 自行定义并训练的 Machine Learning Model | PASS |
| PER / LOC / ORG | PASS |
| 原始英文文本输入及类型/位置输出 | PASS |
| Public GitHub repository | 本仓库 |
| Bonus: Text Redaction | PASS |
| Bonus: Malaysian local synthetic dataset | PASS |
| Bonus: TXT/PDF input | PASS |

## Features

- CPU 可运行的自定义 BiLSTM token classifier。
- 原始英文文本预测、BIO tags、实体类型、token span、字符 `[start,end)`。
- `[PER]`、`[LOC]`、`[ORG]` 自动脱敏。
- Malaysian 姓名、城市、大学、公司、医院与政府机构合成标注数据。
- FastAPI JSON API 和单页 Web 界面。
- UTF-8 `.txt` 与带文本层 `.pdf` 上传；5 MB 限制和错误响应。
- 38 项自动化测试、固定人工挑战矩阵及独立 general/Malaysian test evaluation。

## Model Architecture

`token IDs -> trainable Embedding(64)` 与 `4 casing features -> Linear(8)` 拼接，进入一层双向 LSTM（每方向 96），经过 Dropout 0.25，最后 Linear 输出 8 个 BIO 标签 logits。参数总数 143,536。

没有使用 CRF：采用比赛允许的 BiLSTM Token Classifier 备选，以保证 CPU 和初学者环境可复现。代价是模型没有联合学习 BIO 转移；抽取器会安全修复非法初始 I-tag。

## Dataset

本项目使用可重现的合成英文 BIO 数据，不声称是 CoNLL-2003 或真实用户数据：

- General: 2,400 train / 300 validation / 300 test。
- Malaysian: 160 train / 40 validation / 60 test。
- 标签：`O, B/I-PER, B/I-LOC, B/I-ORG`。
- 完整句子与实体池跨 split 隔离；句法模板仍共享，因此测试指标明显高估真实泛化。

数据由 `src/generate_data.py` 生成，可公开重新分发；仓库不包含受限制的第三方数据集。

## Installation - Windows 11 / PowerShell

需要 64-bit Python 3.11 或 3.12、Git。以下命令已经按本项目结构验证：

```powershell
git clone https://github.com/sleeplessLh/NER-Personal-Information-Detection.git
cd NER-Personal-Information-Detection
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Quick Start

不需要重新训练。仓库中的 checkpoint 会在第一次请求时自动加载到 CPU：

```powershell
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
python -m uvicorn app.main:app --reload
```

打开 <http://127.0.0.1:8000>。停止服务按 `Ctrl+C`。

## Model Prediction

输入 `Sarah works at Microsoft in Kuala Lumpur.`，实际模型返回 `Sarah/PER`、`Microsoft/ORG`、`Kuala Lumpur/LOC` 及字符位置。

```powershell
$body = @{ text = "Sarah works at Microsoft in Kuala Lumpur." } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/predict -Method Post -ContentType "application/json" -Body $body
```

```python
from src.predict import Predictor
result = Predictor().predict("Sarah works at Microsoft in Kuala Lumpur.")
print(result["entities"])
```

## Text Redaction

上述输入的实际脱敏结果为 `[PER] works at [ORG] in [LOC].`。实现按字符 span 从右向左替换，避免位置偏移。

## File Upload

Web 页面可上传 `.txt` 或 `.pdf`。TXT 必须 UTF-8；PDF 必须有文本层；扫描件不支持 OCR；单文件最大 5 MB。无效类型、超大文件、空文件或不可提取 PDF 返回明确 4xx。

## Model Training

Clone 后运行不需要训练。只有重新实验时才执行：

```powershell
python -m src.generate_data
python -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003
python -m src.evaluate
```

训练只合入 general/Malaysian train；validation 用于选模；两个 test split 不参与训练或选模。checkpoint 保存权重、vocabulary、labels、config、seed、数据计数和最佳 epoch。

## Model Evaluation

2026-10-29 在 Windows 11、Python 3.12.15、PyTorch 2.9.0+cpu 重新训练与评估：

- 8 epochs；batch size 64；learning rate 0.003；Adam；seed 42。
- CPU training loop: 15.9974 seconds。
- Best epoch: 6；validation entity F1: 0.9974。
- General synthetic test (300): P/R/F1 = 1.0000/1.0000/1.0000。
- Malaysian synthetic test (60): P/R/F1 = 1.0000/1.0000/1.0000。
- PERSON precision/recall/F1 = 1.0000/1.0000/1.0000 on both synthetic tests。

这些分数只适用于共享模板的合成分布。固定人工挑战矩阵为 11/13 通过；`Petronas executives` 和带括号的句子仍有类型误判，因此不能把合成测试的 1.0 当成生产性能。完整实际输出在 `reports/manual_acceptance.json`。

## Testing

```powershell
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
python -m pytest -q
```

最新实测：`38 passed`。覆盖 dataset、实体池泄漏、preprocessing、vocabulary、BIO、model、forward、loss/backpropagation、checkpoint、prediction、三类实体、标点 span、长文本、重复实体、redaction、Malaysian data、TXT、单页/多页/损坏 PDF、API/Web、空输入、非法/超大文件、CPU inference 与 end-to-end。

## Project Structure

```text
app/main.py                 FastAPI、Web UI、JSON API、TXT/PDF 上传
src/generate_data.py        General/Malaysian 合成 BIO 数据与 split 检查
src/preprocessing.py        Token、字符 span、BIO 校验、vocabulary
src/dataset.py              Dataset、padding、mask、word dropout
src/model.py                自定义 BiLSTM token classifier
src/train.py                Training、validation、checkpoint、history
src/evaluate.py             General/Malaysian 独立 test evaluation
src/predict.py              CPU checkpoint loading、BIO/entity extraction
src/redact.py               基于字符 span 的可靠脱敏
tests/                      38 项自动化测试
models/best_model.pt        已训练 checkpoint；Clone 后直接使用
data/processed/             可分发的合成 general 数据
data/malaysian/             可分发的合成 Malaysian 数据
reports/                    训练与评估 JSON 证据
MODEL_ACCEPTANCE_REPORT.md  完整工程验收记录
```

## Limitations

- 合成模板数据不等于真实 incident report、support chat 或 CoNLL-2003。
- PER/LOC/ORG 不覆盖电话、邮箱、Student ID、Passport、完整地址等所有 PII。
- 无 CRF；非法 BIO 转移主要由后处理修复。
- 不支持扫描 PDF OCR。
- 高风险大学、医院或企业资料必须人工复核，尤其要防止姓名漏检。

## Reproducibility

- 依赖固定在 `pyproject.toml`、`uv.lock`、`requirements.txt`。
- seed 42；每 epoch 指标在 `reports/training_log.json`。
- 测试指标在 `reports/test_metrics.json` 与 `reports/malaysian_test_metrics.json`。
- checkpoint 内含 vocabulary、label mapping 与 model configuration，不依赖外部下载。
- 完整证据和 Clone 验收状态见 `MODEL_ACCEPTANCE_REPORT.md`。

## License

项目源码使用 [MIT License](LICENSE)。仓库中的 general 与 Malaysian 数据均由本项目脚本生成，是用于教学和工程验收的合成数据，不是 CoNLL-2003 或真实个人资料。

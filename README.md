# Student Privacy Protection — Personal Information Detection and Redaction

## Project Overview

这是一个面向英文学生文本的命名实体识别（NER）项目，服务于 Student Incident Reports、Support Chats、Complaints、Feedback、University Administrative Reports 与 Student Activity Reports。模型从随机权重开始训练，由 PyTorch 自定义 `Embedding + casing features + BiLSTM + Linear` 实现，识别 `PERSON (PER)`、`LOCATION (LOC)`、`ORGANISATION (ORG)`，返回字符位置并生成脱敏文本。

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
- Malaysian 学生姓名、地点、大学、学校、学生组织与教育机构合成标注数据。
- FastAPI JSON API 和响应式单页 Web 界面（Input Text、Redact Text、只读结果、Clear）。
- UTF-8 `.txt` 与带文本层 `.pdf` 上传；5 MB 限制和错误响应。
- 47 项自动化测试、13 项学生场景固定挑战矩阵及独立 general/Malaysian test evaluation。

## Model Architecture

`token IDs -> trainable Embedding(64)` 与 `4 casing features -> Linear(8)` 拼接，进入一层双向 LSTM（每方向 96），经过 Dropout 0.25，最后 Linear 输出 8 个 BIO 标签 logits。参数总数 143,536。

没有使用 CRF：采用比赛允许的 BiLSTM Token Classifier 备选，以保证 CPU 和初学者环境可复现。代价是模型没有联合学习 BIO 转移；抽取器会安全修复非法初始 I-tag。

## Dataset

本项目使用可重现的学生场景合成英文 BIO 数据，不声称是 CoNLL-2003、真实学生记录或真实用户数据：

- General: 2,400 train / 300 validation / 300 test。
- Malaysian: 160 train / 40 validation / 60 test。
- 标签：`O, B/I-PER, B/I-LOC, B/I-ORG`。
- 语境覆盖学生报告、投诉、反馈、支持聊天、大学行政报告与学生活动。
- 完整句子与 general/Malaysian 合并实体池跨 split 隔离；句法模板仍共享，因此测试指标高估真实泛化。

数据由 `src/generate_data.py` 生成，可公开重新分发；仓库不包含受限制的第三方数据集。

## Installation - Windows 11 / PowerShell

推荐使用 **Visual Studio Code**，并安装 Microsoft 发布的 Python 扩展。运行项目还需要：

- 64-bit Python 3.11 或 3.12（安装时勾选 `Add Python to PATH`）
- Git for Windows
- PowerShell（Windows 11 已包含）
- Chrome、Edge 或 Firefox 浏览器

不需要 Node.js、npm、React、Vue、数据库、NVIDIA GPU 或重新训练模型。以下命令已经按本项目结构验证：

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

## Web Interface

网页只保留完成任务所需的流程：

1. 在 **Input Text** 输入或粘贴英文学生文本。
2. 点击 **Redact Text**。
3. JavaScript 将原文以 JSON 发送到 `POST /api/redact`。
4. FastAPI 使用仓库中的自训练 checkpoint 推理。
5. **Redacted Text** 只读框显示模型生成的结果。
6. 点击 **Clear** 清空两个文本框。

网页没有 JavaScript 关键词表或姓名硬编码。核心 NER 始终在后端执行。空白、超过 100,000 字符、模型不可用、服务器错误和网络失败都会显示用户可见提示。

也可以直接测试精简 API：

```powershell
$body = @{ text = "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru." } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/redact -Method Post -ContentType "application/json" -Body $body
```

预期响应：

```json
{"redacted_text":"[PER] studies at [ORG] in [LOC]."}
```

## Model Prediction

输入 `Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.`，实际模型返回 `Ahmad Ali/PER`、`Universiti Teknologi Malaysia/ORG`、`Johor Bahru/LOC` 及字符位置。

```powershell
$body = @{ text = "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru." } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/predict -Method Post -ContentType "application/json" -Body $body
```

```python
from src.predict import Predictor
result = Predictor().predict("Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.")
print(result["entities"])
```

## Text Redaction

上述输入的实际脱敏结果为 `[PER] studies at [ORG] in [LOC].`。题目示例句也实际得到 `[PER], a student from [ORG], attended an event in [LOC].`。实现按字符 span 从右向左替换，避免位置偏移。

## File Upload

后端仍保留 `POST /api/upload` 供 TXT/PDF 客户端调用。TXT 必须 UTF-8；PDF 必须有文本层；扫描件不支持 OCR；单文件最大 5 MB。为了保持本次网页极简，主页不显示文件上传控件。

## Model Training

Clone 后运行不需要训练。只有重新实验时才执行：

```powershell
python -m src.generate_data
python -m src.train --epochs 16 --batch-size 64 --learning-rate 0.003
python -m src.evaluate
```

训练只合入 general/Malaysian train；validation 用于选模；两个 test split 不参与训练或选模。checkpoint 保存权重、vocabulary、labels、config、seed、数据计数和最佳 epoch。

## Model Evaluation

2026-10-29 在 Windows 11、Python 3.12.15、PyTorch 2.9.0+cpu 重新训练与评估：

- 16 epochs；batch size 64；learning rate 0.003；Adam；seed 42。
- CPU training loop: 14.2677 seconds。
- Best epoch: 16；validation entity F1: 0.9192。
- General student synthetic test (300): P/R/F1 = 0.9843/1.0000/0.9921。
- Malaysian synthetic test (60): P/R/F1 = 1.0000/1.0000/1.0000。
- PERSON precision/recall/F1 = 1.0000/1.0000/1.0000 on both synthetic tests。

学生场景固定挑战矩阵为 13/13 通过，覆盖 Malaysian 学生姓名、大学、学校、投诉、支持聊天、反馈、活动、重复实体、多句和未知词。它仍是小型人工检查矩阵，不能替代真实学生报告评估。完整实际输出在 `reports/manual_acceptance.json`。

## Testing

```powershell
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
python -m pytest -q
```

最新实测：`47 passed`。覆盖学生数据、合并实体池泄漏、preprocessing、vocabulary、BIO、model、forward、loss/backpropagation、checkpoint、prediction、三类实体、标点 span、长文本、重复实体、redaction、Malaysian data、TXT、单页/多页/损坏 PDF、API/Web、空白/超长输入、连续提交、模型不可用、CPU inference 与 end-to-end。

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
tests/                      47 项自动化测试
models/best_model.pt        已训练 checkpoint；Clone 后直接使用
data/processed/             可分发的合成 general 数据
data/malaysian/             可分发的合成 Malaysian 数据
reports/                    训练与评估 JSON 证据
MODEL_ACCEPTANCE_REPORT.md  完整工程验收记录
```

## Limitations

- 模型针对学生报告、学生支持聊天、投诉、反馈、大学行政报告和学生活动进行优化；不提供医院病人、公司员工或客户场景的专项保证。
- 合成模板数据不等于真实学生 incident report、support chat 或 CoNLL-2003。
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

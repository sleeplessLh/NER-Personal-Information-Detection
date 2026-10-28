# MODEL ACCEPTANCE REPORT

执行日期：2026-10-28（Asia/Singapore）
项目：Personal Information Detection in Text (NER)
目标仓库：<https://github.com/sleeplessLh/NER-Personal-Information-Detection>

## 1. Environment

- OS: Windows 11 sandbox
- Python: 3.12.15
- PyTorch: 2.9.0+cpu
- Device: CPU
- Random seed: 42
- Model parameters: 143,536
- Core framework: PyTorch + FastAPI

## 2. Model Training

实际执行命令：

```powershell
python -m src.generate_data
python -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003
```

- Architecture: trainable Embedding(64) + casing projection(4->8) + one-layer BiLSTM(96 each direction) + Dropout(0.25) + Linear(192->8)
- Optimizer: Adam
- Loss: CrossEntropyLoss，padding label `-100` 被忽略
- Training rows: 2,560（general 2,400 + Malaysian 160）
- Validation rows: 340（general 300 + Malaysian 40）
- Test rows: general 300；Malaysian 60；均未用于训练或选模
- Batch size: 64
- Learning rate: 0.003
- Epochs: 8
- Measured training-loop time: 16.8963 seconds
- Best epoch: 7
- Best validation entity F1: 0.9986225895
- Saved artifact: `models/best_model.pt`（582,645 bytes）
- Checkpoint contents: weights、vocabulary、label mapping、model config、preprocessing config、seed、dataset counts、best epoch/F1

训练从随机初始化开始。未加载预训练 NER 权重，也未调用外部 NER API。采用比赛允许的 BiLSTM Token Classifier 备选而非 CRF；这降低 CPU/教学复杂度，但没有联合 BIO 转移约束。

## 3. Automated Testing

```powershell
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
python -m pytest -q
```

最新结果：**28 passed in 3.37s**（重新训练后的本地验收）。

覆盖 dataset loading、preprocessing、vocabulary、label mapping、BIO validation、model initialization、forward、loss、backpropagation、checkpoint save/load、prediction、PER/LOC/ORG、span、redaction、Malaysian split、TXT/PDF、FastAPI、Web HTML、empty input、invalid/oversized file、CPU inference 与 end-to-end。

## 4. Model Evaluation

实际执行 `python -m src.evaluate`：

| Dataset | Sentences | PER P/R/F1 | LOC F1 | ORG F1 | Overall P/R/F1 |
|---|---:|---:|---:|---:|---:|
| Synthetic general test | 300 | 1.0000 / 1.0000 / 1.0000 | 1.0000 | 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| Synthetic Malaysian test | 60 | 1.0000 / 1.0000 / 1.0000 | 1.0000 | 1.0000 | 1.0000 / 1.0000 / 1.0000 |

内部 F1 >= 0.75 目标达到，PERSON recall 为 1.0000。上述数据实体池和完整句子跨 split 隔离，但仍共享句法模板，因此 1.0 明显高估真实文本泛化。

人工困难句 `Dr. Evelyn Carter emailed the research team from Oxford.` 出现姓名漏检和类型误判。这一失败被保留为真实限制证据。

## 5. Functional Testing

| Function | Actual evidence | Status |
|---|---|---|
| Trained ML model | 8 epochs CPU，checkpoint 可加载 | PASS |
| PER / LOC / ORG | 独立测试指标与真实文本示例 | PASS（合成域） |
| Raw text prediction | `POST /api/predict` | PASS |
| Entity text/type/offset | 返回 token 与字符 span | PASS |
| Redaction | `[PER] works at [ORG] in [LOC].` | PASS |
| Malaysian data | 160/40/60，test 未参与训练 | PASS（合成数据） |
| TXT upload | 真实 Uvicorn multipart 请求返回 3 entities | PASS |
| PDF upload | 真实文本层 PDF 返回 3 entities | PASS |
| Web UI | `/` HTTP 200 且包含 Detect Entities | PASS |
| Invalid/oversized input | 自动化测试验证 4xx | PASS |
| CPU inference | checkpoint 通过 `map_location=cpu` 加载 | PASS |
| Scanned PDF OCR | 明确不支持 | NOT CLAIMED |

真实 Uvicorn 端口 8765 验收：主页 HTTP 200；文本、TXT、PDF 三条路径均返回 3 个实体和 `[PER] works at [ORG] in [LOC].`。服务随后停止。

## 6. Clone Verification

状态：**NOT VERIFIED - 等待首次 GitHub Push 后执行全新 Clone。**

必须在发布后完成：从 GitHub Clone 到新目录、确认 `models/best_model.pt` 存在、使用仓库依赖启动、直接预测与脱敏、TXT/PDF、pytest。未完成前最终项目状态不得标为完全 PASS。

## 7. Known Limitations

- 合成模板数据不等同于 CoNLL-2003、真实 incident report 或 support chat。
- PER/LOC/ORG 不覆盖电话、邮箱、学号、护照、完整地址等所有 PII。
- 无 CRF，BIO 约束主要由后处理安全修复。
- 扫描 PDF 无 OCR。
- 高风险医院、大学、企业脱敏必须人工复核，姓名漏检尤其危险。

## 8. Final Acceptance Status

| Area | Status |
|---|---|
| Model training | PASS |
| Automated tests | PASS |
| ML evaluation | PASS（仅合成模板域） |
| Mandatory model/application requirements | PASS |
| Three bonus features | PASS |
| Public GitHub repository | NOT VERIFIED - 待创建/Push |
| Clean GitHub Clone verification | NOT VERIFIED |
| Production-sensitive-data deployment | FAIL / NOT APPROVED |

当前总状态：**NOT VERIFIED**。只有公开仓库创建、Push 和全新 Clone 验收成功后，才能更新为比赛原型最终 PASS。

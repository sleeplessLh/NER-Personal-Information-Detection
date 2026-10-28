# MODEL ACCEPTANCE REPORT

执行日期：2026-10-28（Asia/Singapore）
平台：Windows 11 sandbox，Python 3.12.15，PyTorch 2.9.0+cpu
结论：教学/比赛原型验收通过；真实敏感资料生产部署验收未通过，也未声称通过。

## 1. Requirement Checklist

| Requirement | Evidence | Result |
|---|---|---|
| 自行训练模型 | `src/model.py` 自定义 Embedding + casing + BiLSTM + Linear；8 epochs CPU 重训 | PASS |
| PER/LOC/ORG | 冻结 test 三类 entity-level F1 均为 1.0000 | PASS（仅合成模板域） |
| 原始英文输入 | `/api/predict` 接收 JSON 文本 | PASS |
| 实体文字/类型/位置 | 返回 `text/type/start/end` 字符区间及 token 区间 | PASS |
| Text Redaction | 从右向左按字符 span 替换，保留原空格、换行、标点 | PASS |
| Malaysian Dataset | 160/40/60，实体池和完整句子跨 split 隔离 | PASS（合成，非真实用户数据） |
| Malaysian 独立评估 | `reports/malaysian_test_metrics.json` | PASS |
| TXT/PDF | UTF-8 TXT、文本 PDF、5 MB 限制、异常处理 | PASS |
| Web/API | FastAPI 页面、JSON endpoint、上传 endpoint | PASS |
| README | 安装、依赖、数据、训练、运行、测试、架构、结果、限制 | PASS |
| 公开 GitHub | 本地仓库尚未发布 | NOT COMPLETED - 需要用户 GitHub 权限 |
| 扫描 PDF OCR | 明确不支持 | NOT CLAIMED |

## 2. Training Evidence

- Command: `.\.venv\Scripts\python.exe -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003`
- Architecture: trainable random Embedding(64) + casing projection(4->8) + one-layer BiLSTM(96 per direction) + Dropout(0.25) + Linear(192->8)
- CRF: 未使用。采用题目允许的 BiLSTM Token Classifier 备选，原因是保持零基础教学与 CPU 复现简单；代价是 BIO 转移约束由后处理修复而非 CRF 联合解码。
- Parameters: 143,536
- Training rows: 2,560（主 2,400 + Malaysian 160）
- Validation rows: 340（主 300 + Malaysian 40）
- Batch size: 64; learning rate: 0.003; optimizer: Adam
- Best epoch: 7; best validation entity-F1: 0.9986225895
- Measured training-loop time: 6.9201 seconds on the provided CPU environment
- Checkpoint: `models/best_model.pt`，包含权重、词表、标签、配置、seed、数据计数和最佳 epoch

## 3. Machine Learning Evaluation

冻结 checkpoint 后执行 `.\.venv\Scripts\python.exe -m src.evaluate`。

| Dataset | Sentences | PER F1 / Recall | LOC F1 | ORG F1 | Overall P/R/F1 |
|---|---:|---:|---:|---:|---:|
| Synthetic general test | 300 | 1.0000 / 1.0000 | 1.0000 | 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| Synthetic Malaysian test | 60 | 1.0000 / 1.0000 | 1.0000 | 1.0000 | 1.0000 / 1.0000 / 1.0000 |

这些结果只说明模型掌握了当前共享句法模板。虽然实体池和完整句子隔离，train/test 仍共享模板分布，所以分数明显高估真实世界泛化。

## 4. Software Tests

Command:

```powershell
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
.\.venv\Scripts\python.exe -m pytest -q --cov=src --cov=app --cov-report=term-missing
```

Result: 核心工程原有 **22 项测试全部保留**；加入 6 项教学用 model V1–V6 演进测试后，完整套件在全新教程复现目录中得到 **28 passed in 3.52s**。低覆盖主要来自训练/数据生成 CLI 的 `main()`，其关键组件和真实 CLI 已分别执行。

覆盖：dataset loading、BIO validation、vocabulary、forward、training step、checkpoint save/load、prediction、span extraction、redaction、empty/invalid input、TXT、PDF、API function response、evaluation、Malaysian split、CPU inference、end-to-end。

## 5. Real HTTP Acceptance

在独立进程启动 Uvicorn 端口 8765，然后 POST `/api/predict`。实际返回 HTTP 成功响应；`John` 的字符区间为 `[0,4)`、`London` 为 `[14,20)`，脱敏结果为 `[PER] lives in [LOC].`。验收后已停止服务。

## 6. Manual Demonstrations

| Input | Actual result | Result |
|---|---|---|
| Farah works at Telekom Malaysia in Cyberjaya. | PER/ORG/LOC，全对 | PASS |
| Kumar studies at Universiti Sains Malaysia in George Town. | PER/ORG/LOC，全对 | PASS |
| Aina met Jason at Hospital Kuala Lumpur. | PER/PER/ORG，全对 | PASS |
| The weather is beautiful today. | 无实体 | PASS |
| Dr. Evelyn Carter emailed the research team from Oxford. | `Dr` 和 `Oxford` 被错误标为 ORG；漏掉 Evelyn Carter | **FAIL - 真实泛化证据** |

## 7. Known Limitations

- 语料由规则模板合成，不等同于 CoNLL-2003 或真实事件报告。
- 当前标签只覆盖 PER/LOC/ORG，不识别电话、邮箱、学号、护照、地址等完整 PII。
- 没有 CRF，模型可能产生非法 BIO 转移；抽取器会修复开头的 I-tag，但不等同于结构化解码。
- 扫描 PDF 没有 OCR。
- 高风险医院、大学或企业脱敏必须人工复核；姓名漏检尤其危险。
- 未发布 GitHub；需要用户审核后自行建立公开仓库。

## 8. Reproduction

```powershell
uv sync --all-groups
uv run python -m src.generate_data
uv run python -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003
uv run python -m src.evaluate
uv run python -m pytest -q
uv run python -m uvicorn app.main:app --reload
```

教程复现范围：已创建全新 `tmp/tutorial-reproduction` 目录，按教程最终状态复制所需文件，使用已锁定并验证的 `.venv` 执行完整测试、评估与预测；结果为 28 passed，确认 general test 300 句、Malaysian test 60 句，并实际返回 Sarah/PER、Microsoft/ORG、Kuala Lumpur/LOC。为避免虚假陈述，本轮没有重新下载依赖、第二次训练 8 epochs、逐字手工键入全部 22 个 Phase，也没有真实初学者试读。

## 9. Tutorial PDF QA

- 最终文件：`output/pdf/NER_From_Zero_To_Complete_Project_CN.pdf`
- 125 页 A4；22 个 Phase 标题全部可提取；所有 125 页均渲染为 PNG。
- 8 张 contact sheet 已逐页总览；封面、环境、数据、模型、API、Phase 20 完整文档与最终页另做原尺寸抽查。
- 自动检查：0 缺失 Phase、0 替换字符、0 未完成占位标记、0 空文本页。
- 视觉检查：中文字体正常；超长源码行使用带 `.... | >` 标记的视觉续行，字符没有被页面裁切；未发现意外空白页或错误页码。
- 可重复证据：`reports/tutorial_pdf_qa.json`；空目录复现证据：`reports/tutorial_reproduction.json`。

# MODEL ACCEPTANCE REPORT

执行日期：2026-10-29（Asia/Singapore）
项目：Personal Information Detection in Text (NER)
仓库：<https://github.com/sleeplessLh/NER-Personal-Information-Detection>

## 1. 核心问题

结论：**YES**。仓库包含已训练的 `models/best_model.pt`。在全新的 Windows 11 目录和虚拟环境中安装 `requirements.txt` 后，可以直接加载模型、预测、脱敏并启动 FastAPI，**不需要重新训练**。这一结论已由修复版本的最终远程 Clone 证明，而不是根据 README 推断。

## 2. 环境与首次 Fresh Clone

- Windows 11 原生环境；PowerShell
- Python 3.12.15；PyTorch 2.9.0+cpu；CPU inference
- 首次审计 Clone：`tmp/full-acceptance-20261029`
- 审计起点 commit：`80b29ae2f36e05d947bd729da11aaa56d4a3e809`
- `python -m venv .venv`：PASS
- `.venv\\Scripts\\python.exe -m pip install -r requirements.txt`：PASS
- 初始仓库测试：28 passed
- 未设置必需环境变量；源码使用项目相对路径

修复 Push 后再次 Clone 到第三个全新目录 `tmp/final-reclone-20261029`：

- 检出功能修复 commit：`7919565e82c2dd147f3acb55eec60613be169165`
- 创建全新 `.venv` 并完整安装 `requirements.txt`：PASS
- `pip check`：`No broken requirements found.`
- checkpoint SHA-256：`4CB9276D78120406F7C2FDD40C2B7F5498659B8E0A5FC3F9C2D7E8657FD15945`
- 未重新训练，直接 CPU 加载、预测和脱敏：PASS
- final Clone tests：**38 passed in 5.40s**
- final Clone Uvicorn：主页、JSON API、TXT、两页 PDF 均 HTTP 200

教程 PDF 构建脚本引用 `C:\\Windows\\Fonts`，这是 Windows 教程制品构建的显式字体依赖，不影响模型、API、测试或 Clone 后运行。运行应用不依赖开发机绝对路径。

## 3. 模型与训练

- Architecture：trainable Embedding(64) + casing projection(4→8) + one-layer BiLSTM(96/方向) + Dropout(0.25) + Linear(192→8)
- Parameters：143,536
- Labels：`<PAD>, O, B/I-PER, B/I-LOC, B/I-ORG`
- Random seed：42；Adam；learning rate 0.003；batch size 64；8 epochs
- Training：general 2,400 + Malaysian 160
- Validation：general 300 + Malaysian 40
- Test：general 300；Malaysian 60；不参与训练或选模
- 本轮训练时间：15.9974 秒（Windows CPU）
- Best epoch：6；best validation entity F1：0.997389
- Checkpoint：585,397 bytes；CPU 可加载
- Checkpoint 内含 weights、vocabulary（178 entries）、label mapping、model config、seed、dataset counts、best epoch/F1

本轮修复了实体池跨 split 重复，并扩充了通用上下文模板。模型仍从随机权重训练，不加载第三方 NER 权重，不调用外部 NER API。

## 4. 独立测试集评估

实际执行 `python -m src.evaluate`：

| Dataset | Sentences | PER Precision | PER Recall | PER F1 | LOC F1 | ORG F1 | Overall P/R/F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Synthetic general test | 300 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| Synthetic Malaysian test | 60 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 / 1.0000 / 1.0000 |

完整句子和实体字符串跨 split 隔离，但模板分布仍共享，所以 1.0 高估真实泛化；它不能被宣传为生产性能。

## 5. 固定真实英文挑战矩阵

实际执行 `python scripts/run_manual_acceptance.py`：**11/13 cases passed**，且全部已预测实体的字符 offset 与原文一致。完整逐例 JSON 在 `reports/manual_acceptance.json`。

成功覆盖美国、印度、中国姓名，陌生地点，大学、医院，mixed/no-entity，重复实体，多句文本和未知词。保留两项真实失败：

1. `Nurul Izzah met Petronas executives in Putrajaya.`：把 `Petronas executives` 误判为 PER。
2. `(John Carter), from Microsoft, visited London!`：漏检括号内姓名，并把 Microsoft 误判为 LOC。

因此项目适合比赛原型展示，但不适合无人复核的真实敏感资料脱敏。

## 6. 自动化、文件与 Web 验收

- `python -m pytest -q`：**38 passed in 3.61s**（修复后开发目录）
- 浏览器真实点击 Detect：显示 3 entities 表格（Sarah/PER、Microsoft/ORG、Kuala Lumpur/LOC）
- 浏览器显示脱敏：`[PER] works at [ORG] in [LOC].`
- 浏览器空输入：显示 `Please enter English text.`
- `GET /`：HTTP 200
- `POST /api/predict`：HTTP 200，3 entities
- TXT：HTTP 200
- 两页 text-layer PDF：HTTP 200，两页文本均提取并进入自训练模型
- 空 TXT：HTTP 400
- 损坏 PDF：HTTP 400
- 不支持 CSV：HTTP 415
- 5 MB 超限文件：HTTP 413
- 空 JSON text：HTTP 422
- 扫描 PDF OCR：不支持，NOT CLAIMED

## 7. 本轮实际修复

1. 纯标点被吸入实体 span：解码时把纯标点 tag 安全归为 `O`，保护字符 offset 和原标点。
2. general validation/test 实体池重复：替换重复 LOC/ORG，并新增自动化 disjoint 测试和生成时失败保护。
3. 陌生上下文泛化弱：新增姓名、地点、大学、医院上下文模板后重新训练；多项人工失败转为正确。
4. Web 页面只打印 JSON：新增实体表格、类型、offset、脱敏区域、状态和错误信息。
5. 未选文件时前端无提示：新增明确提示。
6. 上传内容仅限制文件字节：新增提取文本 100,000 字符上限。
7. 缺少多页/空/损坏 PDF、长文本、重复实体、标点 span 测试：补齐回归覆盖。
8. 缺少 Windows CI：新增 `.github/workflows/windows-tests.yml`。
9. 人工验收不可复现：新增 `scripts/run_manual_acceptance.py` 和实际 JSON 证据。
10. 人工脚本直接运行找不到 `src`：加入可靠项目根目录引导。

## 8. Malaysian Bonus 证据

- 数据存在：160 train / 40 validation / 60 test
- 覆盖 Malaysian 姓名、地点、大学、公司、医院和政府机构
- train/validation/test 实体池与完整句子互斥
- checkpoint `dataset_counts` 明确记录 `malaysian_training=160`、`malaysian_validation=40`
- 独立 Malaysian test entity F1=1.0000（仅合成模板域）
- 数据为合理构造并人工可检查的合成数据，不冒充真实用户数据

## 9. 最终验收矩阵

| 验收项目 | 状态 | 证据 |
|---|---|---|
| Fresh Clone | PASS | 第三个全新目录检出 `7919565`，不重新训练运行 |
| Dependency Installation | PASS | 全新 venv 安装；`pip check` 无冲突 |
| Model Loading | PASS | checkpoint CPU load + inference |
| PERSON Detection | PASS WITH LIMITATION | synthetic PER recall 1.0；人工矩阵有括号姓名漏检 |
| LOCATION Detection | PASS WITH LIMITATION | synthetic LOC F1 1.0；人工样本通过 |
| ORGANISATION Detection | PASS WITH LIMITATION | synthetic ORG F1 1.0；人工矩阵有类型误判 |
| Text Redaction | PASS | offset 回归、重复/多句/标点测试 |
| Malaysian Dataset | PASS WITH LIMITATION | 实际合入训练并独立评估；合成域 |
| TXT Input | PASS | HTTP 200；空文件 400 |
| PDF Input | PASS | 单页/多页 200；损坏 400；无 OCR |
| FastAPI | PASS | 真实 Uvicorn HTTP 请求 |
| Web Interface | PASS | 真实浏览器点击、表格与脱敏可见 |
| Automated Tests | PASS | 38 passed |
| Model Evaluation | PASS WITH LIMITATION | synthetic overall F1 1.0；manual 11/13 |
| Windows 11 | PASS | 本轮为 Windows 11 原生执行；另增 Windows Actions |
| GitHub Sync | PASS | 功能修复 commit `7919565e82c2dd147f3acb55eec60613be169165` |

## 10. 当前 Verdict

**PARTIAL PASS — GitHub 最终功能版本可在全新 Windows 环境直接运行，不需要重新训练；但固定人工挑战矩阵仍有 2/13 项模型泛化失败，因此不能宣布无条件 PASS。**

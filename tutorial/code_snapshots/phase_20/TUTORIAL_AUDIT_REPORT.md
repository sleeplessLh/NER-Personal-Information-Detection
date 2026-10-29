# TUTORIAL AUDIT REPORT

审计日期：2026-10-29（Asia/Singapore）  
对象：`NER_From_Zero_To_Complete_Project_CN.pdf` 与 GitHub `main`  
学生假设：会基础 Python；不知道 ML、PyTorch、NER、虚拟环境或部署。

## 1. 审计方法与证据边界

本次没有把“PDF 很长”或“最终 pytest 通过”当作教学通过。执行了四层验收：

1. **知识顺序审计**：检查新概念是否在首次正式使用前回答是什么、为什么、项目职责、不使用的后果、代码、命令与成功标准。
2. **阶段文件审计**：PDF 的 `PHASE_FILES` 每阶段只交付当时可见文件；禁止 Phase 16 提前展示最终文件上传与网页实现。
3. **阶段式空目录复现**：`scripts/student_reproduction_audit.py` 在 `tmp/NER_Tutorial_Reproduction_Test_2` 中按 Phase 00→21 累积教程文件并逐阶段执行 checkpoint；没有一次复制最终项目，也没有复制开发目录 checkpoint/data/reports。
4. **独立环境/部署验收**：复现目录新建 `.venv`，从 `requirements.txt` 安装 55 packages，`uv pip check` 通过，执行 56 tests；使用该目录实际训练出的 checkpoint 启动 Uvicorn，并在真实浏览器点击 Redact Text。

自动化逐字转录只能证明教程给出的代码和命令足以构建，不等同于真实一年级学生的阅读速度或理解程度。尚未招募独立人类学生做可用性研究，因此“真实人类独立理解”在最终总评中保持 `NOT VERIFIED`，不虚构 PASS。

## 2. 初始版本发现的关键缺陷

| ID | 初始缺陷 | 严重度 | 修复 |
|---|---|---:|---|
| D01 | Phase 06–08、10–21 重复模板话术，概念没有逐阶段具体解释 | Critical | 为 16 个阶段增加专属概念、最小实验、写入顺序、成功条件和错误恢复 |
| D02 | Phase 21 把 PowerShell 命令放进 Python block，还要求 `py_compile` | Critical | 改成真实 `build_pdf.py` Python 代码；PowerShell 验收命令独立显示 |
| D03 | Phase 05 generator 依赖 preprocessing，但 PDF 当时未交付该文件 | Critical | Phase 05 同时完整列出 `preprocessing.py` 与 `generate_data.py` |
| D04 | Phase 07/08/10 的 checkpoint 引用后续或职责过大的测试 | Critical | 新增 `tensor_demo.py`、`dataloader_demo.py`、`training_step_demo.py`，当阶段即可运行 |
| D05 | Phase 16 提前展示最终 `app/main.py`，破坏 API→文件→网页增量 | Critical | 新增 `app_v1_text_api.py`、`app_v2_file_api.py`；Phase 18 才进入最终网页 |
| D06 | Phase 16/17 没有职责隔离的测试 | High | 新增 `test_text_api.py` 与 `test_file_api.py`；Phase 18 新增 `test_web_ui.py` |
| D07 | Web 章节未与最新 `/api/redact`、只读输出、Clear 和可见错误同步 | High | 更新完整 app、调用流程、浏览器 checkpoint 与 README |
| D08 | 原“复现脚本”一次复制最终项目，不能证明阶段可执行 | Critical | 新增阶段式 reproduction audit，真实重新生成 data、训练 16 epochs、评估和部署 |
| D09 | 测试数字和 PDF 证据停留在 47 | Medium | 全部同步为当前 56 tests，并重新生成快照、PDF 与 QA |
| D10 | 没有明确区分技术复现与真实人类学习实验 | High | 报告明确 evidence boundary；人类 novice study 标记 NOT VERIFIED |

## 3. Phase-by-Phase 结果

状态只使用 PASS / FAIL / NOT VERIFIED。

| Phase | Phase Name | Missing Knowledge / Code / Commands（初始） | Fixes Applied | Reproduction Status |
|---:|---|---|---|---|
| 00 | 项目边界与成果 | 无关键缺失 | 保留范围、限制、学习方法与最终示例 | PASS |
| 01 | Windows/Python/VS Code/venv | 无关键缺失 | 复测 Python 版本、PATH、venv、pip、CPU PyTorch、首文件 | PASS |
| 02 | Python 基础 | 无关键缺失 | class/object/type hint 与实体 dict 实验可运行 | PASS |
| 03 | NLP/NER/BIO | 无关键缺失 | token/entity/sequence/BIO 边界小实验可运行 | PASS |
| 04 | 骨架/config/Git | 快照没有代表 PDF 全文件 | 以 PDF PHASE_FILES 为准交付 pyproject/.gitignore/constants | PASS |
| 05 | Dataset | generator 的 preprocessing 前置断层 | 同阶段交付 preprocessing；真实生成 2400/300/300 与 160/40/60 | PASS |
| 06 | Token/BIO/Vocabulary | 通用模板；测试文件未在阶段展示 | 专属 span/UNK/PAD/BIO/casing 解释并交付 test_preprocessing | PASS |
| 07 | Tensor/ID/Padding | 直接进入 Dataset，缺独立 dtype/shape 观察 | 新增 tensor_demo；明确 long/float/bool 与 (L,4) | PASS |
| 08 | Dataset/DataLoader | checkpoint 依赖后续 model test | 新增 dataloader_demo；验证 padding/mask，无模型依赖 | PASS |
| 09 | Embedding/LSTM/BiLSTM | 无关键缺失 | 保留 V1→V6 六个真实可运行版本与 shape tests | PASS |
| 10 | Loss/Backprop | 通用片段且引用 acceptance test | 新增独立 training_step_demo；真实 weight change | PASS |
| 11 | Epoch/Validation/Checkpoint | Malaysian merge 的数据来源说明不足 | 补 train/eval/no_grad/checkpoint 契约与数据计数；真实训练 16 epochs | PASS |
| 12 | Loading/Prediction/BIO decode | 通用模板 | 增加 CPU map、eval/no_grad、argmax、char span 逐步数据流 | PASS |
| 13 | Redaction | 通用模板 | 增加半开区间、逆序替换、空格/换行实验 | PASS |
| 14 | Malaysian integration | 合成伦理与 test 隔离解释不足 | 增加 160/40/60 检查、checkpoint counts 与泄漏边界 | PASS |
| 15 | Evaluation | Precision/Recall/F1 只有定义 | 增加数值实验、exact span、token accuracy 陷阱与双 test 报告 | PASS |
| 16 | Text API | 提前展示最终 app；缺独立 API 版本 | 创建 app_v1 + test_text_api；真实 request/redact/cache 教学 | PASS |
| 17 | TXT/PDF | 与最终 app 混杂 | 创建 app_v2 + test_file_api；明确 bytes/UTF-8/PDF/OCR/400/413/415 | PASS |
| 18 | Web Interface | 旧 Detect/Upload UI 与最新简易 UI 不一致 | 最终 app 只保留 Input/Redact/Output/Clear；真实浏览器点击 | PASS |
| 19 | Tests/Debug | 通用模板；没有阶段测试层级 | 明确 unit/integration/E2E 与失败缩小顺序；56 tests | PASS |
| 20 | README/GitHub | 测试数与环境说明旧 | 更新 IDE、依赖、启动、API、证据和 GitHub 边界 | PASS |
| 21 | Final reproduction | 无效 Python block；旧脚本整包复制 | 改为阶段式审计、新 venv、训练、测试、Uvicorn、浏览器、PDF QA | PASS |

## 4. Fresh Reproduction Evidence

- 目录：`tmp/NER_Tutorial_Reproduction_Test_2`
- 阶段：22/22 PASS；逐阶段证据：`reports/student_phase_reproduction.json`
- Dataset：在复现目录由 Phase 05 命令重新生成
- Model：在复现目录 CPU 重新训练 16 epochs；没有复制开发 checkpoint
- Environment：全新 `.venv`；55 packages installed；`uv pip check` PASS
- Tests：56 passed in 21.80s（新环境）
- Evaluation：general student 300 + Malaysian student 60
- Deployment：复现目录的 Uvicorn `127.0.0.1:8776`
- Browser：输入 Ahmad Ali 示例，实际显示 `[PER] studies at [ORG] in [LOC].`
- PDF：最终版 141/141 页已渲染；22 个 Phase 标题齐全，0 个替代字符、0 个空白文本页；结果见 `reports/tutorial_pdf_qa.json`

## 5. Final Criteria

| Criterion | Status | Evidence / Remaining Issue |
|---|---|---|
| A Learning Completeness | PASS（结构审计） | 新概念、实验、正式代码、成功/失败条件均存在 |
| B Coding Completeness | PASS | 阶段式目录 22/22 |
| C Environment Completeness | PASS | 新 `.venv`、55 dependencies、pip check |
| D Training Completeness | PASS | 新目录真实 16-epoch CPU training |
| E Deployment Completeness | PASS | 新目录 Uvicorn + real browser |
| F Documentation Consistency | PASS | 22 Phase validator、20 path synchronization 与 141-page PDF QA 均已通过 |
| G Fresh Reproduction | PASS（工程模拟） | 逐阶段而非整包复制；真实人类学习实验不包含在内 |
| Independent novice human study | NOT VERIFIED | 当前没有独立一年级学生参与者 |

## 6. Audit Verdict

**PARTIAL PASS**：从空目录开始的阶段式工程复现、全新环境安装、重新训练、56 tests、评估和浏览器部署均已通过；但是“真实零 ML 基础的人类学生无需任何帮助即可理解并完成”尚未由独立人类参与者实测，因此不能诚实宣布完整 PASS。

若要把最后一项升级为 PASS，必须安排至少一名符合画像的学生只使用最终 PDF 操作，记录每次求助、错误与耗时；出现任何必须外部搜索或猜测的步骤就回到相应 Phase 修订并复测。

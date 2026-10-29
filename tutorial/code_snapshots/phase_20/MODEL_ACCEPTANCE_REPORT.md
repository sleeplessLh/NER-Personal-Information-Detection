# MODEL ACCEPTANCE REPORT — STUDENT PRIVACY PROTECTION

执行日期：2026-10-29（Asia/Singapore）
仓库：<https://github.com/sleeplessLh/NER-Personal-Information-Detection>

## 1. Scope

项目应用范围已限定为 **Student Personal Information Detection and Redaction**，重点处理英文 Student Incident Reports、Student Support Chats、Student Complaints、Student Feedback、University Administrative Reports 与 Student Activity Reports。

模型仍识别比赛要求的 `PERSON`、`LOCATION`、`ORGANISATION`，没有简化成只识别学生姓名。医院病人、公司员工、客户等非学生场景不再作为专项优化目标。

## 2. Model and Training

- Architecture：Embedding(64) + casing projection(4→8) + one-layer BiLSTM(96/方向) + Dropout(0.25) + Linear(192→8)
- Parameters：143,536
- Labels：`<PAD>, O, B/I-PER, B/I-LOC, B/I-ORG`
- Training：general student 2,400 + Malaysian student 160
- Validation：general student 300 + Malaysian student 40
- Test：general student 300 + Malaysian student 60；不参与训练或选模
- Adam；learning rate 0.003；batch size 64；seed 42
- Epochs：16；best epoch：16
- Best validation entity F1：0.919245
- Windows CPU training-loop time：14.2677 seconds
- Checkpoint：`models/best_model.pt`，586,229 bytes
- SHA-256：`C0F68A78DD13599229EDA6C42799C84D68FF3942FAC600E8B5626571DB6F3575`

Checkpoint 含 weights、vocabulary、labels、model configuration、seed、dataset counts、best epoch/F1。模型从随机权重训练，不调用外部 NER API，不加载现成 NER pipeline。

## 3. Student Data

训练语境覆盖学生报告、投诉、反馈、支持聊天、大学行政报告、学生组织和学生活动。实体池重点覆盖 Malaysian student names、universities、schools、student organisations 和 Malaysian locations。

数据生成阶段和自动化测试同时验证：

- 完整句子跨 split 隔离
- general 与 Malaysian 合并实体池跨 train/validation/test 隔离
- test 不参与训练或 validation 选模
- 数据为透明的合成数据，不声称等同于真实学生记录

## 4. Evaluation

实际执行 `python -m src.evaluate`：

| Dataset | PER P/R/F1 | LOC P/R/F1 | ORG P/R/F1 | Overall P/R/F1 |
|---|---:|---:|---:|---:|
| General student synthetic test（300） | 1.0000 / 1.0000 / 1.0000 | 0.9408 / 1.0000 / 0.9695 | 1.0000 / 1.0000 / 1.0000 | 0.9843 / 1.0000 / 0.9921 |
| Malaysian student synthetic test（60） | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |

Overall F1 ≥ 0.75 与 PERSON Recall ≥ 0.80 的内部目标均达到。模板仍跨 split 共享，因此指标会高估真实学生文本泛化。

## 5. Student Challenge Matrix

实际执行 `python scripts/run_manual_acceptance.py`：**13/13 passed**。

覆盖：

- Malaysian 与国际学生姓名
- Malaysian university、school 与 location
- Student complaint、support chat、feedback、activity、administrative report
- Mixed PER/LOC/ORG
- No entity
- Repeated student names
- Multiple sentences
- Punctuation
- Unknown student/university/location names

全部预测实体满足 `original_text[start:end] == entity_text`。完整输出保存在 `reports/manual_acceptance.json`。

题目示例实际输出：

```text
Original: Ahmad Ali, a student from Universiti Teknologi Malaysia, attended an event in Johor Bahru.
Redacted: [PER], a student from [ORG], attended an event in [LOC].
```

## 6. Software, Web and File Tests

- Automated tests：**39 passed in 4.06s**（开发目录）
- Windows browser：Student Privacy Protection 页面正常显示
- 浏览器点击 Detect：3 entities，PER/ORG/LOC 表格与 offset 正确
- 浏览器 Redacted Text：题目示例完全匹配
- `POST /api/predict`：HTTP 200，3 entities
- Student-report TXT：HTTP 200，脱敏正确
- Two-page student PDF：HTTP 200，两页均提取并送入自训练模型
- Empty/corrupt/unsupported/oversized files：400/415/413 回归测试覆盖
- CPU inference：PASS
- Scanned PDF OCR：NOT CLAIMED

## 7. Changes for Student Scope

1. README、FastAPI title、Web description、demo text 与 presentation 改为 Student Privacy Protection。
2. general 与 Malaysian 数据池改为学生姓名、大学、学校、学生组织、教育机构和地点。
3. 模板改为 incident、complaint、feedback、support、activity 和 administration 语境。
4. 增加 general/Malaysian 合并实体池跨 split 泄漏保护。
5. 增加单词姓名与重复学生姓名结构，不使用姓名硬编码替代训练。
6. 重新生成全部数据，实际训练 16 epochs 并替换 checkpoint。
7. 将 API、Web、prediction、redaction、TXT、PDF 测试示例切换为学生场景。
8. 将固定人工验收矩阵完全重写为 13 个学生隐私场景。

## 8. Acceptance Matrix

| Item | Status | Evidence |
|---|---|---|
| Student scope | PASS | README/data/UI/tests updated |
| Trained ML checkpoint | PASS | 16 epochs CPU；checkpoint load |
| PERSON | PASS | synthetic recall 1.0；student matrix |
| LOCATION | PASS | general F1 0.9695；Malaysian F1 1.0 |
| ORGANISATION | PASS | both synthetic F1 1.0 |
| Student redaction | PASS | exact Ahmad Ali example |
| Malaysian student data | PASS WITH LIMITATION | trained/evaluated synthetic dataset |
| TXT/PDF | PASS | real localhost requests |
| Web interface | PASS | real browser click and visible table |
| Automated tests | PASS | 39 passed |
| GitHub update | PENDING | awaiting commit/push |
| Final remote re-clone | PENDING | execute after push |
| Production deployment | NOT APPROVED | requires real student data and human review |

## 9. Limitations

- 合成学生文本不等于真实大学 incident reports 或 support chats。
- 小型 13-case challenge matrix 不等于大规模独立真实语料评估。
- PER/LOC/ORG 不覆盖 email、phone、student ID、passport、完整地址等所有学生 PII。
- 扫描 PDF 无 OCR。
- 高风险学生资料必须人工复核，尤其要防止姓名漏检。
- 非学生场景没有专项性能保证。

## 10. Current Verdict

**PENDING FINAL RE-CLONE — 本地学生场景代码、训练、评估、Web、TXT/PDF 与测试已通过；必须 Push 后从 GitHub 全新 Clone 才能最终放行。**

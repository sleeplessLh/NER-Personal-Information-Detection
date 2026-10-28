# Acceptance Report

执行日期：2026-10-28（Asia/Singapore）

## 自动化测试

命令：`.\.venv\Scripts\python.exe -m pytest -q --cov=src --cov=app --cov-report=term-missing`

结果：`15 passed, 1 warning in 13.92s`。warning 来自 Starlette TestClient 对 AnyIO alias 的弃用提示，不影响功能。

## Level A 功能验收

| Test | Expected | Actual / Evidence | Result |
|---|---|---|---|
| 真实训练 | 产生参数更新与 checkpoint | 4 轮日志；最终 141,232 参数元素 | PASS |
| checkpoint 重载 | 新进程可加载 | evaluate、pytest、两次 Uvicorn 进程均加载 | PASS |
| 未见原始文本 | 返回实体 JSON | 独立测试实体列表与训练分离 | PASS（限合成分布） |
| 三种实体 | PER/LOC/ORG | 自动化与手动样例均覆盖 | PASS |
| 自动脱敏 | 占位符输出 | `[PER] works at [ORG] in [LOC].` | PASS |
| API | HTTP JSON | `/api/predict` TestClient + Uvicorn | PASS |
| 无实体 | 空实体数组 | `The weather is beautiful today.` -> `[]` | PASS |
| 多实体 | 全部返回 | Sarah 样例返回 3 个实体 | PASS |
| 重复实体 | 分别替换 | redaction 单元测试 | PASS |
| 标点 | 正确 token 与输出空格 | tokenizer/redaction 测试 | PASS |
| TXT | UTF-8 提取并推理 | API 测试 | PASS |
| 文本 PDF | 提取并推理 | ReportLab 动态 PDF API 测试 | PASS |
| 服务重启 | 重启后可推理 | 端口 8765/8766 两进程均返回 3 实体 | PASS |
| 扫描 PDF OCR | 非最低要求 | 未实现 | NOT CLAIMED |

## Manual Testing

| Input | Expected | Actual | Result |
|---|---|---|---|
| John lives in London. | John/PER, London/LOC | 完全一致 | PASS |
| Ali studies at Universiti Teknologi Malaysia. | Ali/PER, UTM/ORG | 完全一致 | PASS |
| Sarah works at Microsoft in Kuala Lumpur. | Sarah/PER, Microsoft/ORG, Kuala Lumpur/LOC | 完全一致 | PASS |
| The weather is beautiful today. | 无实体 | 空数组 | PASS |
| Ahmad met Siti at Universiti Malaya. | Ahmad/PER, Siti/PER, UM/ORG | 完全一致 | PASS |

## Level B 性能验收

- Overall entity-level F1：1.0000 >= 0.80，PASS
- PERSON recall：1.0000 >= 0.85，PASS

此结论严格限定于当前合成独立 test split。模板生成方式使 train/test 共享句法模板，即使实体与完整句子分离，难度仍低于真实数据。项目功能和教学验收通过，但生产级真实世界泛化尚未验证。

## 未完成的外部验证

- 没有真实初学者参与试读，因此不得声称 Condition 15 已通过真实用户可理解性测试；教程提供 checkpoint questions 与可执行验证步骤作为替代证据。
- 未发布到 GitHub；用户需自行审核后发布。

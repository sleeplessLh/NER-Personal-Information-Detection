# Phase 1：需求分析

## Requirement Checklist

| 类别 | 必须交付 | 验收方式 |
|---|---|---|
| 核心模型 | 自行定义并训练的 PyTorch Embedding + BiLSTM + Linear token classifier | checkpoint 元数据、训练日志、参数与梯度测试 |
| 实体类型 | PERSON、LOCATION、ORGANISATION | 独立测试集 entity-level 指标与手动样例 |
| 原始文本 | 输入任意文本并返回实体与类型 | CLI、Python API、FastAPI 集成测试 |
| 脱敏 | 用 `[PERSON]` 等占位符替换实体 | 单元测试与 API 测试 |
| 马来西亚数据 | 公开机构/地点与合成人名，不使用真实敏感信息 | 数据卡、质量检查、分割泄漏检查 |
| 文件上传 | TXT 与文本型 PDF | 自动化测试 |
| Web | FastAPI + HTML/CSS/JS | TestClient 与重启加载测试 |
| 可复现性 | 固定 seed、锁定依赖、保存全部推理配置 | 清洁进程加载、复训命令 |
| 文档 | README、环境/训练/验收报告、中文 PDF | 代码一致性检查、PDF 渲染检查 |

## Proposed Architecture

```text
Raw text -> deterministic tokenizer -> token IDs -> Embedding
         -> bidirectional LSTM -> Linear classifier -> BIO tags
         -> entity span extraction -> JSON + redacted text
```

采用自己定义的 BiLSTM token classifier，不调用第三方 NER 服务或现成 NER pipeline。Padding token 的 loss 使用 `ignore_index` 排除。训练期间以 validation entity-level F1 选择最佳 checkpoint，test set 只在模型冻结后评估。

## Dataset Plan

1. 主数据：优先使用合法可获得、带 PER/LOC/ORG BIO 标签的公开英文 NER 数据，下载后记录来源、许可证、哈希与原始格式。
2. 本地扩展：程序化生成并人工审阅小型马来西亚语境样本。人名明确标记为合成示例；机构和地点使用公开名称。
3. 标签统一：将所有标签映射到 `O/B-PER/I-PER/B-LOC/I-LOC/B-ORG/I-ORG`。
4. 分割：先按句子规范化文本去重，再固定 seed 分割；任何规范化文本不得跨 split。
5. 质量：验证 token/label 等长、BIO 转移合法、标签集合一致、无重复泄漏。

## Environment Plan

- 实际验收环境：本机 Windows 11、项目内 `.venv`、CPU 或可用 CUDA（以实际检测为准）。
- 依赖：用 `pyproject.toml` 与 `uv.lock` 锁定；导出 `requirements.txt`。
- 所有报告仅将实际执行过的版本标记为“已验证”。
- PDF 使用 ReportLab 生成、Poppler 渲染为 PNG，并逐页检查关键布局与中文字体。

## Acceptance Criteria

### Level A：功能

用户列出的 14 项功能要求全部进入自动化/手动验收矩阵，包括模型重载、无实体、多实体、重复实体、标点、TXT/PDF、API 与服务重启。

### Level B：性能

- Overall entity-level F1 目标：>= 0.80
- PERSON recall 目标：>= 0.85

指标按精确 span + 类型匹配计算。若未达标，将如实标记“性能验收未通过”，保留实验与误差分析，不修改 test set 或泄漏标签。

## 关键风险

- 从零训练的 word-level BiLSTM 对 OOV 名称敏感；将评估是否加入 character-level encoder。只有验证数据证明必要时才增加。
- 小型马来西亚合成集可能高估真实泛化能力；报告将分开呈现公开测试集与本地挑战集。
- 扫描 PDF 不做 OCR；仅支持含可提取文本的 PDF。

# Phase 05：建立并验证一般与 Malaysian 数据集

## 1. 本阶段学习目标

理解 supervised dataset、sample、split、JSONL、synthetic data、data leakage；使用 `src/generate_data.py` 真实生成 2400/300/300 一般数据和 160/40/60 Malaysian 数据。任何完整句跨 split 重复时命令必须失败。

## 2. 本阶段需要掌握的知识

Training/validation/test 的不同职责；template 与 entity pool；随机数 seed；JSON 与 JSONL；人工规则标注；为什么合成数据不等同真实用户数据；为什么实体不重复仍不能消除 template distribution bias。

## 3. 从零解释知识点

每个 sample 是 dict：`text:str`、`tokens:list[str]`、`labels:list[str]`。JSONL 每行一个独立 JSON object，便于流式读取和定位坏行。Training 更新 weights；validation 选 epoch；test 只在冻结后评估。

合成数据通过 template 插入已知实体，因此可准确生成 label，但语言多样性有限。我们分开 train/validation/test entity pools，并检查规范化完整句交集；仍共享 grammar templates，所以 1.0 F1 会高估真实世界。Malaysia 名称池包含公开机构/地点和虚构姓名，不包含私人资料。

## 4. 本阶段开始前的项目状态

```text
src/constants.py       [已有]
src/generate_data.py   [本阶段新增]
data/processed/        [运行后生成]
data/malaysian/        [运行后生成]
tests/                 [本阶段增加数据检查]
```

## 5. 本阶段需要使用的工具

VS Code 打开 generator；PowerShell 根目录运行 module；Explorer 可抽查 JSONL，但不要用 Excel 自动改编码。使用 `python -m src.generate_data` 而非双击文件，保证 package import 正确。

### 6. Lesson 05.1：设计 sample 与 `_annotate`

先手写一个 sample：

```python
{"tokens": ["Ali", "works", "at", "Maybank", "."],
 "labels": ["B-PER", "O", "O", "B-ORG", "O"]}
```

`_annotate(rendered, values)` 先 `split()` 得 token，再建立等长 O list，寻找实体 token slice，首项写 B，后续写 I，最后调用 `validate_bio`。Parameters 是 rendered str 与 type->value dict；return 是含 tokens/labels/text 的 dict；调用者是 split generator。

### 7. Lesson 05.2：独立 entity pools 与 deterministic random

定义 `ENTITY_POOLS['train'|'validation'|'test']`。同一个人名不跨 pool。`random.Random(seed)` 创建局部 RNG，不污染全局。每条样本选择 template 与 pool value；相同 seed 应产生相同文件，便于复现。

运行小测试：

```powershell
python -c "from src.generate_data import generate_split; a=generate_split('test',3,42); b=generate_split('test',3,42); assert a==b; print('PASS')"
```

### 8. Lesson 05.3：Malaysian 独立 split

`MALAYSIAN_POOLS` 同样分三组。`generate_malaysian_split` 使用 local templates，输出 160 train、40 validation、60 test。测试集绝不在 `train.py` 的 training rows 中。规则标注仍需人工抽样；真实扩展应双人标注与解决分歧。

不能声称“人工真实数据”：这里是规则生成合成句。README、报告和 PDF 都必须用相同措辞。

### 9. Lesson 05.4：写 JSONL 与 leakage fail-fast

`_write_jsonl` 使用 UTF-8，每个 row `json.dumps(...,ensure_ascii=False)` 后换行。main 对每 split 建 lowercase text set，与先前 sets 求交；只要 overlap 非空就 raise RuntimeError，不静默删除。

执行：

```powershell
python -m src.generate_data
Get-Content data\processed\summary.json
```

真实输出 rows：2400/300/300 与 Malaysian 160/40/60；unique sentences 少于 rows 是 split 内模板组合重复，不是跨 split 泄漏。跨 split 交集已检查为零。

## 10. 完整代码回顾

打开 `src/generate_data.py`：imports -> pools/templates -> annotate -> general/local generators -> writer -> main。确认 main 只写数据，不 import model/train。最终文件较长，应按函数阅读而非一次记忆。

## 11. 跨文件调用关系

generator import constants paths 和 preprocessing.validate_bio；main 调 generate -> annotate -> validate -> write。后续 dataset.load_jsonl 读取结果；train 只读 train/validation；evaluate 只读 test。

## 12. 数据流解释

template str + entity values -> rendered str -> tokens list -> labels list -> sample dict -> JSON string -> `.jsonl` bytes。Summary 将 rows/unique counts 写 JSON。没有 Tensor，数据仍是 Python/磁盘层。

## 13. 常见错误

实体 substring 重叠导致错误边界；PER2 未单独标注；同一 neutral sentence 跨 split；test pool 被 training import；默认 ASCII 使中文转义；忘记换行；看到高分却忽略模板共享。使用断言、交集和人工抽查修复。

## 14. Checkpoint

```powershell
python -m src.generate_data
python -c "from src.dataset import load_jsonl; from src.constants import PROCESSED_DIR,MALAYSIAN_DIR; assert len(load_jsonl(PROCESSED_DIR/'train.jsonl'))==2400; assert len(load_jsonl(MALAYSIAN_DIR/'test.jsonl'))==60; print('PASS')"
```

再检查每 row tokens/labels 等长、标签合法、train/test text set disjoint。实际生成命令已退出 0。

## 15. 学生练习

新增一个不含实体 template；人工抽查 20 行；统计三类实体数量；故意复制一句到 test 验证 fail-fast；解释 unique<rows 为什么不必然是跨 split leakage。

## 16. 面试准备

"I generated transparent synthetic BIO data with separate entity pools and exact-sentence leakage checks. Malaysian train, validation and test are separate. The splits still share templates, so I explicitly limit claims about real-world generalization."

## 17. 下一阶段预告

Phase 06 正式实现 tokenizer、字符 span、BIO validator、vocabulary、UNK 与 casing features，并用独立测试处理异常输入。

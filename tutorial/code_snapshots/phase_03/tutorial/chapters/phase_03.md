# Phase 03：从零认识 NLP、NER 与 BIO

## 1. 本阶段学习目标

你会创建 `learning/bio_demo.py`，手工写出 token 与 BIO label，验证标注合法性，并把连续标签合并为实体。这里没有神经网络：先完全理解“模型未来要预测的答案长什么样”。

完成后你必须能解释 token、sequence、label、entity、span、B/I/O，并能指出 `I-ORG` 为什么不能无缘无故出现在句首。

## 2. 本阶段需要掌握的知识

- Natural Language Processing (NLP) 与 Named Entity Recognition (NER)。
- Sequence labeling：为序列中每个 token 预测一个 label。
- Token 不等于单纯按空格分词；标点也可成为 token。
- BIO：Begin、Inside、Outside。
- Entity span 使用 `[start_token,end_token)` 半开区间。
- Sentinel：循环末尾临时添加 `O`，统一关闭最后实体。

## 3. 从零解释知识点

NLP 是让计算机处理人类语言的领域。NER 是其中一个任务：找出有名称的实体并分类。输入句子是 sequence，模型输出等长 label sequence。

句子 `Ali studies at Universiti Malaya.` 可拆成 `Ali`, `studies`, `at`, `Universiti`, `Malaya`, `.`。`Ali` 是单 token PER；机构有两个 token。BIO 标注为 `B-PER O O B-ORG I-ORG O`。B 表示新实体开始，I 表示同类型实体继续，O 表示不属于目标实体。

如果只有 `ORG` 而没有 B/I，就难以区分相邻的两个实体。规范 BIO 中 `I-LOC` 必须紧跟 B-LOC 或 I-LOC；gold data 出现非法 I 时应拒绝，而不是悄悄训练。

## 4. 本阶段开始前的项目状态

```text
learning/
  hello_python.py             [已有]
  python_foundations.py       [已有]
  bio_demo.py                 [本阶段新增]
tutorial/chapters/phase_03.md [本阶段新增]
```

`src/preprocessing.py` 还没有创建；Phase 06 会把本阶段概念升级为正式实现。

## 5. 本阶段需要使用的工具

在 VS Code Explorer 的 `learning` 下新建 `bio_demo.py`。Integrated Terminal 必须位于项目根目录并激活 `.venv`。本阶段只使用 Python 标准库，不需要 torch。

### 6. Lesson 03.1：手工建立 token/label 对齐

先写：

```python
tokens = ["Ali", "studies", "at", "Universiti", "Malaya", "."]
labels = ["B-PER", "O", "O", "B-ORG", "I-ORG", "O"]
print(list(zip(tokens, labels, strict=True)))
```

`zip` 把相同位置配对。`strict=True` 在两个 list 长度不同时抛错，避免静默丢数据。运行临时版本，预期看到六个 tuple。若你的 Python 低于 3.10 不支持 strict，这也是为什么环境要求 3.11/3.12。

逐项读：index 0 `Ali/B-PER`；index 3 `Universiti/B-ORG`；index 4 `Malaya/I-ORG`。标点是 O。

### 7. Lesson 03.2：实现 `validate_bio`

首先定义允许类型：

```python
ALLOWED_TYPES = {"PER", "LOC", "ORG"}
```

Set 适合 membership 检查。然后创建函数，先检查长度，再用 `previous_type` 记录前一个实体类型。遇到 O 时清空；遇到 B/I 时用 `split('-',1)` 分开 prefix/type。

关键判断：

```python
if prefix == "I" and previous_type != entity_type:
    raise ValueError(f"illegal I-tag at {index}: {label}")
```

Function parameters 都是 `list[str]`；正常返回 `None`，代表“验证通过无需产生新数据”；异常输入 raise ValueError。调用者是 `bio_to_entities`，后者必须先验证再处理。

局部测试：

```powershell
python -c "from learning.bio_demo import validate_bio; validate_bio(['Ali'], ['B-PER']); print('PASS')"
```

错误测试：

```powershell
python -c "from learning.bio_demo import validate_bio; validate_bio(['Malaysia'], ['I-LOC'])"
```

第二条实际应以 `ValueError: illegal I-tag at 0: I-LOC` 失败。失败是正确行为。

### 8. Lesson 03.3：把 BIO 合并为 entity

函数签名：

```python
def bio_to_entities(tokens: list[str], labels: list[str]) -> list[dict[str, str | int]]:
```

输入来自手工列表；正式项目中 labels 来自模型。返回 list，每个 dict 包含 text/type/start_token/end_token。内部 `start` 初始 None，代表没有打开实体。

循环使用：

```python
for index, label in enumerate(labels + ["O"]):
```

最后额外 O 是 sentinel。如果最后一个 token 属于实体，sentinel 会触发保存；它不写回原 labels。遇到 B 或 O 时先关闭旧实体，再决定是否打开新实体。

文字由 `" ".join(tokens[start:index])` 合并。end_token 是 exclusive，所以 tokens[start:end] 正好得到实体。

### 9. Lesson 03.4：实际运行与检查输出

创建 main，使用上一节例子并打印。执行：

```powershell
python learning\bio_demo.py
```

真实输出结构：

```text
[('Ali', 'B-PER'), ('studies', 'O'), ('at', 'O'), ('Universiti', 'B-ORG'), ('Malaya', 'I-ORG'), ('.', 'O')]
[{'text': 'Ali', 'type': 'PER', 'start_token': 0, 'end_token': 1}, {'text': 'Universiti Malaya', 'type': 'ORG', 'start_token': 3, 'end_token': 5}]
```

检查 `tokens[3:5]` 是两个机构 token。若 entity 没有保存，检查 sentinel 与循环缩进。

## 10. 完整代码回顾

打开 `learning/bio_demo.py`，确认顺序是 module docstring -> allowed types -> validate -> bio_to_entities -> main -> main guard。不要把 validation 删除后只保留 happy path；错误数据必须尽早失败。

## 11. 跨文件调用关系

`main()` 准备 tokens/labels -> 调用 `bio_to_entities()` -> 该函数先调用 `validate_bio()` -> 验证通过后合并 -> entities 返回 main -> print。Phase 06 的 `src/preprocessing.py` 会采用同样约束；Phase 15 的 metrics 会把 BIO 转 exact spans。

## 12. 数据流解释

输入原句概念上是 str，但本阶段手工提供 `list[str]`。labels 是等长 list[str]。validate 不改变数据。bio_to_entities 用 integer index 跟踪边界，返回 `list[dict]`。此时 span 是 token 位置，不是原始字符位置；字符 span 在 Phase 13 实现。

## 13. 常见错误

1. token/label 长度不同：先逐项 zip 检查。
2. `I-ORG` 跟在 `B-PER`：实体类型不连续，应改 B-ORG。
3. 忘记最后 sentinel：句尾实体丢失。
4. end 当 inclusive：Python slice 少/多一个 token；统一使用 exclusive。
5. 将 LOC 与 ORG 混淆：依据标注 guideline，而不是凭大小写。
6. 把 token span 当 character span：它们单位不同。

## 14. Checkpoint

执行：

```powershell
python -m py_compile learning\bio_demo.py
python learning\bio_demo.py
python -c "from learning.bio_demo import bio_to_entities; print(bio_to_entities(['Kuala','Lumpur'],['B-LOC','I-LOC']))"
```

通过条件：编译成功；主例得到两个实体；最后命令得到一个 text=`Kuala Lumpur`、type=`LOC`、span `[0,2)` 的实体。再运行非法 I 测试，必须抛 ValueError。

## 15. 学生练习

1. 标注 `Ahmad studies at Universiti Malaya in Kuala Lumpur.`。
2. 构造包含两个相邻 PER 的合法 BIO。
3. 故意制造长度不等并解释错误。
4. 给 validate 增加未知标签 `B-MISC` 的失败测试。
5. 解释为什么 O 会关闭当前实体。

## 16. 面试准备

"NER is a sequence-labeling task. Each token receives a BIO tag. B starts an entity, I continues the same entity type, and O means outside. I validate gold BIO sequences before training and use half-open token spans to reconstruct entities."

## 17. 下一阶段预告

Phase 04 会创建正式项目骨架、`src/constants.py`、`.gitignore` 和测试入口。手工 BIO 概念随后在 Phase 05/06 用于真实 JSONL 数据生成、校验和 vocabulary。

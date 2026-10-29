# Phase 14：Malaysian 数据合入训练与独立测试

## 1. 本阶段学习目标

本阶段围绕 `src/train.py` 完成一个可独立验收的功能。为什么现在需要它：仅创建本地文件不算 Bonus；必须用于训练并单独评估，且 test 不可泄漏。 完成后学生必须能说明输入、输出、参数、返回值、调用者和下一步消费者，而不只是复制代码。

## 2. 本阶段需要掌握的知识

local-domain adaptation、split isolation、dataset merge、synthetic ethics、checkpoint dataset counts。第一次出现时先在 Lesson 1 用普通 Python/具体数值理解，再进入正式文件。

## 3. 从零解释知识点

Domain adaptation 是把目标场景数据加入训练，而不是写关键词名单。General 与 Malaysian split 使用独立实体池，防止同一名字跨 split 泄漏。extend 只合并 train/train 与 validation/validation；local test 始终冻结。合成数据可公开和检查，但不能冒充真实学生记录。

学习顺序固定为：先做可丢弃的小实验，确认具体输入/输出；再按写入顺序完成正式函数；最后运行本阶段 checkpoint。完整源码会在本阶段末尾逐行列出，不能只复制两个片段后跳到下一章。

## 4. 本阶段开始前的项目状态

```text
src/train.py                 [本阶段新增或修改]
tests/                 [本阶段增加/运行对应测试]
tutorial/chapters/phase_14.md [同步更新]
tutorial/code_snapshots/phase_14/ [通过后生成]
```

上一阶段文件保持不变，除非 Lesson 明确指出修改位置。不要提前复制下一阶段代码。

## 5. 本阶段需要使用的工具

打开 VS Code Explorer，定位 `src/train.py`；Terminal -> New Terminal 打开 PowerShell；确认 Working Directory 是项目根目录，prompt 有 `(.venv)`。先执行 `python --version`，再按 Lesson 输入。所有命令默认在根目录、已激活 `.venv`。

### 6. Lesson 14.1：先理解概念和接口

本阶段新概念：local-domain adaptation、split isolation、dataset merge、synthetic ethics、checkpoint dataset counts。先不要修改正式文件。在项目根目录执行这个最小实验：

```powershell
python -c "from src.dataset import load_jsonl; from src.constants import MALAYSIAN_DIR; print([len(load_jsonl(MALAYSIAN_DIR/f'{s}.jsonl')) for s in ('train','validation','test')])"
```

通过条件：输出 [160,40,60]；checkpoint training=2560、validation=340；搜索 train.py 不存在读取 Malaysian test 的代码。

### 7. Lesson 14.2：编写第一个最小单元

在 VS Code 打开 `src/train.py`。若文件不存在就按该路径新建；若已存在，先用 Ctrl+F 查找代码块中的第一个 `class`/`def`/变量名，并在完整源码显示的相同顺序写入。不要凭感觉选择位置。先输入：

```python
local_train_rows = load_jsonl(MALAYSIAN_DIR / "train.jsonl")
local_validation_rows = load_jsonl(MALAYSIAN_DIR / "validation.jsonl")
train_rows.extend(local_train_rows)
validation_rows.extend(local_validation_rows)
```

逐行检查 import、变量 scope、parameter type 和 return。这是局部代码，不代表完整文件；正式写入顺序如下：在 train.main 中读取 general train/validation 后，分别读取 local train/validation 并 extend。Vocabulary 只从合并训练集建立。把四个计数写入 checkpoint，evaluate 才单独读取 local test。

### 8. Lesson 14.3：连接下一个逻辑单元

在上一段已经通过后，再加入：

```python
"dataset_counts": {"training": len(train_rows), "validation": len(validation_rows),
 "malaysian_training": len(local_train_rows),
 "malaysian_validation": len(local_validation_rows)}
```

新增代码读取上一单元的返回值，而不是重新计算或使用全局隐藏状态。用具体 sample 手工追踪一遍数据；记录每个 list/dict/Tensor/str 的类型。若涉及 Tensor，打印 shape/dtype 后再接下一层。

### 9. Lesson 14.4：立即运行并记录真实结果

在项目根目录运行：

```powershell
python -c "import torch; c=torch.load('models/best_model.pt',weights_only=False); print(c['dataset_counts'])"
```

本项目真实证据：checkpoint 记录 training=2560、validation=340、Malaysian training=160、validation=40；test=60 未进入。 学生电脑的时间可能不同，但结构、断言和文件数量应一致。命令失败时保留完整 traceback，从最后一行向上找第一个自己的文件行号；修复后重跑同一命令。

## 10. 完整代码回顾与函数契约

本阶段 PDF 紧接着列出 `src/train.py` 的完整验收版本（带真实行号并分块，不能省略）。学生必须在 VS Code 中按 Lesson 顺序输入，而不是从 GitHub 偷看下一阶段。完成后运行 `python -m py_compile src/train.py`；无错误只证明文件可读取/语法正确，还必须通过第 9/14 节的功能测试。

函数契约检查法：对本阶段每个 `def`/`class` 写五行笔记：输入参数与类型、返回值与类型、直接调用者、它调用的项目函数、失败方式。若完整源码出现 Lesson 未提到的函数，停下并在该函数 docstring 和调用处补完笔记后再继续。

## 11. 跨文件调用关系

general/local train 合并 -> vocabulary/DataLoader；general/local validation 合并选模；两个 test 仅 evaluate。 调用关系必须与 imports 一致：上游只提供数据，下游消费返回值；不要建立 circular import。学生在纸上画箭头，并在箭头写真实 function name 与 return type。

## 12. 数据流解释

general/local train 合并 -> vocabulary/DataLoader；general/local validation 合并选模；两个 test 仅 evaluate。 对每一步写下：输入类型、shape/长度、是否修改原对象、输出交给谁。出现 Tensor 时使用 `(batch,sequence,features)` 具体数字；出现字符 span 时使用 `[start,end)`。

## 13. 常见错误

把 local test extend 到 train；声称合成名字是真实用户；只测试 challenge.txt；跨 pool 同名；文档计数不同步。 排错顺序：确认工作目录和解释器 -> 阅读 traceback -> 打印最小输入/type/shape -> 单独运行当前 Lesson 测试 -> 修复根因 -> 跑本章与全套回归。禁止用删除测试或宽泛 except 制造通过。

## 14. Checkpoint

执行 Lesson 4 命令并保存输出。再口头解释本章新增函数的 parameters、return、调用者和被调用函数。代码测试与口头解释都通过才生成 phase snapshot；只有其中之一不算完成。

## 15. 学生练习

1. 用新的最小输入重复本章函数并预测输出。2. 故意制造一个第 13 节错误，保存 traceback 与修复。3. 给关键函数添加一个边界断言。4. 画跨文件调用图。5. 不看教程重新输入最小代码单元。

## 16. 面试准备

I merged only Malaysian train and validation. The local test split stayed unseen and was evaluated separately after freezing.

回答时先说目的，再说输入/输出，最后用实际测试证据和限制收尾；不要背诵库名称。

## 17. 下一阶段预告

Phase 15 计算两个 test 的 exact entity metrics，并保留失败案例。

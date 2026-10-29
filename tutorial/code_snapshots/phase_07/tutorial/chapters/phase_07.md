# Phase 07：Tensor、Token ID、特征与 Padding

## 1. 本阶段学习目标

本阶段围绕 `src/dataset.py` 完成一个可独立验收的功能。为什么现在需要它：PyTorch layer 接收 Tensor；学生必须在 DataLoader 前理解每个维度，而不是把 shape 当魔法。 完成后学生必须能说明输入、输出、参数、返回值、调用者和下一步消费者，而不只是复制代码。

## 2. 本阶段需要掌握的知识

Tensor、dtype、shape、dimension、long/float/bool、token ID、feature vector、padding、mask。第一次出现时先在 Lesson 1 用普通 Python/具体数值理解，再进入正式文件。

## 3. 从零解释知识点

Tensor 是带 dtype 和 shape 的多维数字容器。Embedding 的索引必须是 torch.long；手工特征必须是 float32；mask 用 bool。B 表示 batch 句数，L 表示当前句长，M 表示 batch 最大长度。若 dtype 或维度错误，错误会在 Embedding、Linear 或 loss 才爆发，难以定位，所以本阶段先独立打印。

学习顺序固定为：先做可丢弃的小实验，确认具体输入/输出；再按写入顺序完成正式函数；最后运行本阶段 checkpoint。完整源码会在本阶段末尾逐行列出，不能只复制两个片段后跳到下一章。

## 4. 本阶段开始前的项目状态

```text
src/dataset.py                 [本阶段新增或修改]
tests/                 [本阶段增加/运行对应测试]
tutorial/chapters/phase_07.md [同步更新]
tutorial/code_snapshots/phase_07/ [通过后生成]
```

上一阶段文件保持不变，除非 Lesson 明确指出修改位置。不要提前复制下一阶段代码。

## 5. 本阶段需要使用的工具

打开 VS Code Explorer，定位 `src/dataset.py`；Terminal -> New Terminal 打开 PowerShell；确认 Working Directory 是项目根目录，prompt 有 `(.venv)`。先执行 `python --version`，再按 Lesson 输入。所有命令默认在根目录、已激活 `.venv`。

### 6. Lesson 07.1：先理解概念和接口

本阶段新概念：Tensor、dtype、shape、dimension、long/float/bool、token ID、feature vector、padding、mask。先不要修改正式文件。在项目根目录执行这个最小实验：

```powershell
python -c "import torch; ids=torch.tensor([2,5,1],dtype=torch.long); f=torch.zeros((3,4),dtype=torch.float32); print(ids,ids.dtype,ids.shape); print(f.dtype,f.shape)"
```

通过条件：输出 ids dtype=torch.int64 shape=[3]，features dtype=torch.float32 shape=[3,4]；单样本字段类型与教程表格一致。

### 7. Lesson 07.2：编写第一个最小单元

在 VS Code 打开 `src/dataset.py`。若文件不存在就按该路径新建；若已存在，先用 Ctrl+F 查找代码块中的第一个 `class`/`def`/变量名，并在完整源码显示的相同顺序写入。不要凭感觉选择位置。先输入：

```python
input_ids = torch.tensor(tokens_to_ids(row["tokens"], vocabulary), dtype=torch.long)
features = torch.tensor(casing_features(row["tokens"]), dtype=torch.float32)
labels = torch.tensor([label_to_id[x] for x in row["labels"]], dtype=torch.long)
```

逐行检查 import、变量 scope、parameter type 和 return。这是局部代码，不代表完整文件；正式写入顺序如下：在 NERDataset.__getitem__ 中只转换一条 row：tokens 保留为 list[str]，input_ids/labels 为 (L,)，features 为 (L,4)。不要在这里 padding；padding 属于下一阶段 collate_batch。

### 8. Lesson 07.3：连接下一个逻辑单元

在上一段已经通过后，再加入：

```python
input_ids = torch.zeros((batch_size, max_length), dtype=torch.long)
features = torch.zeros((batch_size, max_length, 4), dtype=torch.float32)
labels = torch.zeros((batch_size, max_length), dtype=torch.long)
mask = torch.zeros((batch_size, max_length), dtype=torch.bool)
```

新增代码读取上一单元的返回值，而不是重新计算或使用全局隐藏状态。用具体 sample 手工追踪一遍数据；记录每个 list/dict/Tensor/str 的类型。若涉及 Tensor，打印 shape/dtype 后再接下一层。

### 9. Lesson 07.4：立即运行并记录真实结果

在项目根目录运行：

```powershell
python -m learning.tensor_demo
```

本项目真实证据：数据读取与 Tensor forward shape 测试通过。 学生电脑的时间可能不同，但结构、断言和文件数量应一致。命令失败时保留完整 traceback，从最后一行向上找第一个自己的文件行号；修复后重跑同一命令。

## 10. 完整代码回顾与函数契约

本阶段 PDF 紧接着列出 `src/dataset.py` 的完整验收版本（带真实行号并分块，不能省略）。学生必须在 VS Code 中按 Lesson 顺序输入，而不是从 GitHub 偷看下一阶段。完成后运行 `python -m py_compile src/dataset.py`；无错误只证明文件可读取/语法正确，还必须通过第 9/14 节的功能测试。

函数契约检查法：对本阶段每个 `def`/`class` 写五行笔记：输入参数与类型、返回值与类型、直接调用者、它调用的项目函数、失败方式。若完整源码出现 Lesson 未提到的函数，停下并在该函数 docstring 和调用处补完笔记后再继续。

## 11. 跨文件调用关系

tokens list -> IDs list -> long Tensor `(L,)`; casing -> float Tensor `(L,4)`；padding 后 `(B,M)`/`(B,M,4)`。 调用关系必须与 imports 一致：上游只提供数据，下游消费返回值；不要建立 circular import。学生在纸上画箭头，并在箭头写真实 function name 与 return type。

## 12. 数据流解释

tokens list -> IDs list -> long Tensor `(L,)`; casing -> float Tensor `(L,4)`；padding 后 `(B,M)`/`(B,M,4)`。 对每一步写下：输入类型、shape/长度、是否修改原对象、输出交给谁。出现 Tensor 时使用 `(batch,sequence,features)` 具体数字；出现字符 span 时使用 `[start,end)`。

## 13. 常见错误

Embedding 收到 float；features 最后一维不是 4；label 使用字符串；padding 后没有 mask；把 batch/length 顺序颠倒。 排错顺序：确认工作目录和解释器 -> 阅读 traceback -> 打印最小输入/type/shape -> 单独运行当前 Lesson 测试 -> 修复根因 -> 跑本章与全套回归。禁止用删除测试或宽泛 except 制造通过。

## 14. Checkpoint

执行 Lesson 4 命令并保存输出。再口头解释本章新增函数的 parameters、return、调用者和被调用函数。代码测试与口头解释都通过才生成 phase snapshot；只有其中之一不算完成。

## 15. 学生练习

1. 用新的最小输入重复本章函数并预测输出。2. 故意制造一个第 13 节错误，保存 traceback 与修复。3. 给关键函数添加一个边界断言。4. 画跨文件调用图。5. 不看教程重新输入最小代码单元。

## 16. 面试准备

Token IDs and labels use int64, numeric features use float32, and the mask uses bool. Padding makes variable-length sentences form one rectangular batch.

回答时先说目的，再说输入/输出，最后用实际测试证据和限制收尾；不要背诵库名称。

## 17. 下一阶段预告

Phase 08 用 Dataset/DataLoader 自动索引、shuffle 和 collate。

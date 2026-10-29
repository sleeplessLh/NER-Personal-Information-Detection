# Phase 10：Loss、Gradient、Backpropagation 与 Training Step

## 1. 本阶段学习目标

本阶段围绕 `src/train.py` 完成一个可独立验收的功能。为什么现在需要它：模型结构只有随机参数；training step 才让参数根据 gold labels 改变。 完成后学生必须能说明输入、输出、参数、返回值、调用者和下一步消费者，而不只是复制代码。

## 2. 本阶段需要掌握的知识

logit、CrossEntropyLoss、loss、gradient、computational graph、zero_grad、backward、optimizer.step、gradient clipping。第一次出现时先在 Lesson 1 用普通 Python/具体数值理解，再进入正式文件。

## 3. 从零解释知识点

Logit 是未归一化类别分数；CrossEntropyLoss 直接接收 logits 与正确 label ID。gradient 表示参数微小变化对 loss 的影响。zero_grad 清除上一轮梯度，backward 只计算梯度，optimizer.step 才修改参数。clip_grad_norm_ 限制 LSTM 梯度爆炸。若先 argmax，离散结果不能提供训练需要的梯度。

学习顺序固定为：先做可丢弃的小实验，确认具体输入/输出；再按写入顺序完成正式函数；最后运行本阶段 checkpoint。完整源码会在本阶段末尾逐行列出，不能只复制两个片段后跳到下一章。

## 4. 本阶段开始前的项目状态

```text
src/train.py                 [本阶段新增或修改]
tests/                 [本阶段增加/运行对应测试]
tutorial/chapters/phase_10.md [同步更新]
tutorial/code_snapshots/phase_10/ [通过后生成]
```

上一阶段文件保持不变，除非 Lesson 明确指出修改位置。不要提前复制下一阶段代码。

## 5. 本阶段需要使用的工具

打开 VS Code Explorer，定位 `src/train.py`；Terminal -> New Terminal 打开 PowerShell；确认 Working Directory 是项目根目录，prompt 有 `(.venv)`。先执行 `python --version`，再按 Lesson 输入。所有命令默认在根目录、已激活 `.venv`。

### 6. Lesson 10.1：先理解概念和接口

本阶段新概念：logit、CrossEntropyLoss、loss、gradient、computational graph、zero_grad、backward、optimizer.step、gradient clipping。先不要修改正式文件。在项目根目录执行这个最小实验：

```powershell
python -c "import torch; from torch import nn; x=torch.tensor([[1.,2.]],requires_grad=True); loss=nn.CrossEntropyLoss()(x,torch.tensor([0])); loss.backward(); print(round(loss.item(),4)); print(x.grad)"
```

通过条件：loss 是有限正数；x.grad 不是 None；training-step 测试确认至少一个模型参数发生变化。

### 7. Lesson 10.2：编写第一个最小单元

在 VS Code 打开 `src/train.py`。若文件不存在就按该路径新建；若已存在，先用 Ctrl+F 查找代码块中的第一个 `class`/`def`/变量名，并在完整源码显示的相同顺序写入。不要凭感觉选择位置。先输入：

```python
criterion = nn.CrossEntropyLoss(ignore_index=label_to_id["<PAD>"])
optimizer = Adam(model.parameters(), lr=0.003)
optimizer.zero_grad()
logits = model(input_ids, features)
loss = criterion(logits.reshape(-1, logits.shape[-1]), labels.reshape(-1))
```

逐行检查 import、变量 scope、parameter type 和 return。这是局部代码，不代表完整文件；正式写入顺序如下：在 run_epoch 的训练分支严格按 zero_grad -> forward -> loss -> backward -> clip -> step 排列。先在 1 个 batch 上保存 classifier.weight.clone()，step 后比较，确认参数真的改变，再写 epoch loop。

### 8. Lesson 10.3：连接下一个逻辑单元

在上一段已经通过后，再加入：

```python
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
optimizer.step()
```

新增代码读取上一单元的返回值，而不是重新计算或使用全局隐藏状态。用具体 sample 手工追踪一遍数据；记录每个 list/dict/Tensor/str 的类型。若涉及 Tensor，打印 shape/dtype 后再接下一层。

### 9. Lesson 10.4：立即运行并记录真实结果

在项目根目录运行：

```powershell
python -m learning.training_step_demo
```

本项目真实证据：测试保存 classifier weight 前副本；一步训练后不相等，PASS。 学生电脑的时间可能不同，但结构、断言和文件数量应一致。命令失败时保留完整 traceback，从最后一行向上找第一个自己的文件行号；修复后重跑同一命令。

## 10. 完整代码回顾与函数契约

本阶段 PDF 紧接着列出 `src/train.py` 的完整验收版本（带真实行号并分块，不能省略）。学生必须在 VS Code 中按 Lesson 顺序输入，而不是从 GitHub 偷看下一阶段。完成后运行 `python -m py_compile src/train.py`；无错误只证明文件可读取/语法正确，还必须通过第 9/14 节的功能测试。

函数契约检查法：对本阶段每个 `def`/`class` 写五行笔记：输入参数与类型、返回值与类型、直接调用者、它调用的项目函数、失败方式。若完整源码出现 Lesson 未提到的函数，停下并在该函数 docstring 和调用处补完笔记后再继续。

## 11. 跨文件调用关系

batch -> logits -> cross entropy 与 gold 比较 -> scalar loss -> gradients -> Adam 更新 parameters。 调用关系必须与 imports 一致：上游只提供数据，下游消费返回值；不要建立 circular import。学生在纸上画箭头，并在箭头写真实 function name 与 return type。

## 12. 数据流解释

batch -> logits -> cross entropy 与 gold 比较 -> scalar loss -> gradients -> Adam 更新 parameters。 对每一步写下：输入类型、shape/长度、是否修改原对象、输出交给谁。出现 Tensor 时使用 `(batch,sequence,features)` 具体数字；出现字符 span 时使用 `[start,end)`。

## 13. 常见错误

忘记 zero_grad 导致累积；先 argmax 再 loss；padding 参与 loss；只 backward 不 step；在 validation 更新参数。 排错顺序：确认工作目录和解释器 -> 阅读 traceback -> 打印最小输入/type/shape -> 单独运行当前 Lesson 测试 -> 修复根因 -> 跑本章与全套回归。禁止用删除测试或宽泛 except 制造通过。

## 14. Checkpoint

执行 Lesson 4 命令并保存输出。再口头解释本章新增函数的 parameters、return、调用者和被调用函数。代码测试与口头解释都通过才生成 phase snapshot；只有其中之一不算完成。

## 15. 学生练习

1. 用新的最小输入重复本章函数并预测输出。2. 故意制造一个第 13 节错误，保存 traceback 与修复。3. 给关键函数添加一个边界断言。4. 画跨文件调用图。5. 不看教程重新输入最小代码单元。

## 16. 面试准备

Backward computes gradients but does not update weights. Adam updates them in optimizer.step, after gradients are cleared and computed.

回答时先说目的，再说输入/输出，最后用实际测试证据和限制收尾；不要背诵库名称。

## 17. 下一阶段预告

Phase 11 把一个 step 扩展为 epoch、validation 和 checkpoint。

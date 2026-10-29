# Phase 13：字符 Span 与可靠 Text Redaction

## 1. 本阶段学习目标

本阶段围绕 `src/redact.py` 完成一个可独立验收的功能。为什么现在需要它：重拼 token 会改变双空格/换行；应用必须保留未识别原文。 完成后学生必须能说明输入、输出、参数、返回值、调用者和下一步消费者，而不只是复制代码。

## 2. 本阶段需要掌握的知识

half-open character span、string slicing、right-to-left replacement、offset stability、format preservation。第一次出现时先在 Lesson 1 用普通 Python/具体数值理解，再进入正式文件。

## 3. 从零解释知识点

字符 span [start,end) 的 end 不包含最后字符，正好适配 Python slicing。替换会改变字符串长度，因此必须从 start 最大的实体向左替换；这样尚未处理的左侧 offset 不变。str.replace 不可靠，因为它会替换同名但未预测的位置。

学习顺序固定为：先做可丢弃的小实验，确认具体输入/输出；再按写入顺序完成正式函数；最后运行本阶段 checkpoint。完整源码会在本阶段末尾逐行列出，不能只复制两个片段后跳到下一章。

## 4. 本阶段开始前的项目状态

```text
src/redact.py                 [本阶段新增或修改]
tests/                 [本阶段增加/运行对应测试]
tutorial/chapters/phase_13.md [同步更新]
tutorial/code_snapshots/phase_13/ [通过后生成]
```

上一阶段文件保持不变，除非 Lesson 明确指出修改位置。不要提前复制下一阶段代码。

## 5. 本阶段需要使用的工具

打开 VS Code Explorer，定位 `src/redact.py`；Terminal -> New Terminal 打开 PowerShell；确认 Working Directory 是项目根目录，prompt 有 `(.venv)`。先执行 `python --version`，再按 Lesson 输入。所有命令默认在根目录、已激活 `.venv`。

### 6. Lesson 13.1：先理解概念和接口

本阶段新概念：half-open character span、string slicing、right-to-left replacement、offset stability、format preservation。先不要修改正式文件。在项目根目录执行这个最小实验：

```powershell
python -c "from src.redact import redact_text; t='Alice  studies.\n'; e=[{'text':'Alice','type':'PER','start':0,'end':5}]; print(repr(redact_text(t,e)))"
```

通过条件：输出 repr 为 '[PER]  studies.\n'，双空格与换行原样保留；redaction tests 全部通过。

### 7. Lesson 13.2：编写第一个最小单元

在 VS Code 打开 `src/redact.py`。若文件不存在就按该路径新建；若已存在，先用 Ctrl+F 查找代码块中的第一个 `class`/`def`/变量名，并在完整源码显示的相同顺序写入。不要凭感觉选择位置。先输入：

```python
def redact_text(text, entities):
    redacted = text
    for entity in sorted(entities, key=lambda item: item["start"], reverse=True):
        redacted = redacted[:entity["start"]] + f"[{entity['type']}]" + redacted[entity["end"]:]
    return redacted
```

逐行检查 import、变量 scope、parameter type 和 return。这是局部代码，不代表完整文件；正式写入顺序如下：先验证每个 span 的边界与非重叠，再 sorted(..., reverse=True)；循环中只修改 redacted 副本，不修改 text 或 entities。API 的 analyze 是调用者。

### 8. Lesson 13.3：连接下一个逻辑单元

在上一段已经通过后，再加入：

```python
assert original[entity["start"]:entity["end"]] == entity["text"]
assert redact_text("Alice  works.\n", [{"type":"PER","start":0,"end":5}]) == "[PER]  works.\n"
```

新增代码读取上一单元的返回值，而不是重新计算或使用全局隐藏状态。用具体 sample 手工追踪一遍数据；记录每个 list/dict/Tensor/str 的类型。若涉及 Tensor，打印 shape/dtype 后再接下一层。

### 9. Lesson 13.4：立即运行并记录真实结果

在项目根目录运行：

```powershell
python -m pytest tests\test_redaction.py -q
```

本项目真实证据：多 token、重复实体、双空格和换行保留测试全部通过。 学生电脑的时间可能不同，但结构、断言和文件数量应一致。命令失败时保留完整 traceback，从最后一行向上找第一个自己的文件行号；修复后重跑同一命令。

## 10. 完整代码回顾与函数契约

本阶段 PDF 紧接着列出 `src/redact.py` 的完整验收版本（带真实行号并分块，不能省略）。学生必须在 VS Code 中按 Lesson 顺序输入，而不是从 GitHub 偷看下一阶段。完成后运行 `python -m py_compile src/redact.py`；无错误只证明文件可读取/语法正确，还必须通过第 9/14 节的功能测试。

函数契约检查法：对本阶段每个 `def`/`class` 写五行笔记：输入参数与类型、返回值与类型、直接调用者、它调用的项目函数、失败方式。若完整源码出现 Lesson 未提到的函数，停下并在该函数 docstring 和调用处补完笔记后再继续。

## 11. 跨文件调用关系

entities with char offsets + original str -> descending replacements -> new redacted str；原输入不修改。 调用关系必须与 imports 一致：上游只提供数据，下游消费返回值；不要建立 circular import。学生在纸上画箭头，并在箭头写真实 function name 与 return type。

## 12. 数据流解释

entities with char offsets + original str -> descending replacements -> new redacted str；原输入不修改。 对每一步写下：输入类型、shape/长度、是否修改原对象、输出交给谁。出现 Tensor 时使用 `(batch,sequence,features)` 具体数字；出现字符 span 时使用 `[start,end)`。

## 13. 常见错误

从左向右导致 offset 漂移；end inclusive；重叠 entities；用 token index slice 字符串；重新 join tokens。 排错顺序：确认工作目录和解释器 -> 阅读 traceback -> 打印最小输入/type/shape -> 单独运行当前 Lesson 测试 -> 修复根因 -> 跑本章与全套回归。禁止用删除测试或宽泛 except 制造通过。

## 14. Checkpoint

执行 Lesson 4 命令并保存输出。再口头解释本章新增函数的 parameters、return、调用者和被调用函数。代码测试与口头解释都通过才生成 phase snapshot；只有其中之一不算完成。

## 15. 学生练习

1. 用新的最小输入重复本章函数并预测输出。2. 故意制造一个第 13 节错误，保存 traceback 与修复。3. 给关键函数添加一个边界断言。4. 画跨文件调用图。5. 不看教程重新输入最小代码单元。

## 16. 面试准备

I use half-open character spans and replace from right to left, so earlier offsets stay valid and untouched formatting is preserved.

回答时先说目的，再说输入/输出，最后用实际测试证据和限制收尾；不要背诵库名称。

## 17. 下一阶段预告

Phase 14 明确把 Malaysian train/validation 合入训练，test 保持冻结。

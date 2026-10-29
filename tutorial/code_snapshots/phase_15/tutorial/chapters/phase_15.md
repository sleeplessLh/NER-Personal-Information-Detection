# Phase 15：Entity-level Evaluation、失败案例与限制

## 1. 本阶段学习目标

本阶段围绕 `src/evaluate.py` 完成一个可独立验收的功能。为什么现在需要它：pytest 证明软件可运行，不证明实体预测好；必须冻结 checkpoint 后量化。 完成后学生必须能说明输入、输出、参数、返回值、调用者和下一步消费者，而不只是复制代码。

## 2. 本阶段需要掌握的知识

TP/FP/FN、precision、recall、F1、exact span、per-class、person recall、distribution shift、token accuracy limitation。第一次出现时先在 Lesson 1 用普通 Python/具体数值理解，再进入正式文件。

## 3. 从零解释知识点

TP 要求实体类型和完整边界都相同；FP 是多报，FN 是漏报。Precision 关心报出的有多少正确，Recall 关心真实实体找回多少，F1 是两者调和平均。Token accuracy 会被大量 O 标签抬高，不能单独评价 NER。PERSON recall 对学生隐私尤其重要。

学习顺序固定为：先做可丢弃的小实验，确认具体输入/输出；再按写入顺序完成正式函数；最后运行本阶段 checkpoint。完整源码会在本阶段末尾逐行列出，不能只复制两个片段后跳到下一章。

## 4. 本阶段开始前的项目状态

```text
src/evaluate.py                 [本阶段新增或修改]
tests/                 [本阶段增加/运行对应测试]
tutorial/chapters/phase_15.md [同步更新]
tutorial/code_snapshots/phase_15/ [通过后生成]
```

上一阶段文件保持不变，除非 Lesson 明确指出修改位置。不要提前复制下一阶段代码。

## 5. 本阶段需要使用的工具

打开 VS Code Explorer，定位 `src/evaluate.py`；Terminal -> New Terminal 打开 PowerShell；确认 Working Directory 是项目根目录，prompt 有 `(.venv)`。先执行 `python --version`，再按 Lesson 输入。所有命令默认在根目录、已激活 `.venv`。

### 6. Lesson 15.1：先理解概念和接口

本阶段新概念：TP/FP/FN、precision、recall、F1、exact span、per-class、person recall、distribution shift、token accuracy limitation。先不要修改正式文件。在项目根目录执行这个最小实验：

```powershell
python -c "tp,fp,fn=8,2,4; p=tp/(tp+fp); r=tp/(tp+fn); print(p,r,2*p*r/(p+r))"
```

通过条件：命令生成两个报告，句数为 300/60，包含 PER/LOC/ORG/overall 的 tp/fp/fn/precision/recall/f1。

### 7. Lesson 15.2：编写第一个最小单元

在 VS Code 打开 `src/evaluate.py`。若文件不存在就按该路径新建；若已存在，先用 Ctrl+F 查找代码块中的第一个 `class`/`def`/变量名，并在完整源码显示的相同顺序写入。不要凭感觉选择位置。先输入：

```python
precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
```

逐行检查 import、变量 scope、parameter type 和 return。这是局部代码，不代表完整文件；正式写入顺序如下：metrics.py 先把 BIO 转成 (type,start,end) set，再计数；evaluate.py 加载冻结 Predictor，对 general test 与 Malaysian test 分开调用并分别写 JSON。不要在 evaluate 中 optimizer.step。

### 8. Lesson 15.3：连接下一个逻辑单元

在上一段已经通过后，再加入：

```python
predicted = [predictor.predict_tokens(row["tokens"]) for row in rows]
metrics = entity_metrics(gold, predicted)
save_json(report, REPORTS_DIR / "test_metrics.json")
```

新增代码读取上一单元的返回值，而不是重新计算或使用全局隐藏状态。用具体 sample 手工追踪一遍数据；记录每个 list/dict/Tensor/str 的类型。若涉及 Tensor，打印 shape/dtype 后再接下一层。

### 9. Lesson 15.4：立即运行并记录真实结果

在项目根目录运行：

```powershell
python -m src.evaluate
```

本项目真实证据：一般 synthetic test 300 句与 Malaysian test 60 句均 1.0；手动 Dr. Evelyn Carter/Oxford 样例失败，证明模板泛化限制。 学生电脑的时间可能不同，但结构、断言和文件数量应一致。命令失败时保留完整 traceback，从最后一行向上找第一个自己的文件行号；修复后重跑同一命令。

## 10. 完整代码回顾与函数契约

本阶段 PDF 紧接着列出 `src/evaluate.py` 的完整验收版本（带真实行号并分块，不能省略）。学生必须在 VS Code 中按 Lesson 顺序输入，而不是从 GitHub 偷看下一阶段。完成后运行 `python -m py_compile src/evaluate.py`；无错误只证明文件可读取/语法正确，还必须通过第 9/14 节的功能测试。

函数契约检查法：对本阶段每个 `def`/`class` 写五行笔记：输入参数与类型、返回值与类型、直接调用者、它调用的项目函数、失败方式。若完整源码出现 Lesson 未提到的函数，停下并在该函数 docstring 和调用处补完笔记后再继续。

## 11. 跨文件调用关系

frozen checkpoint + gold test -> predicted BIO -> exact sets -> TP/FP/FN -> per-class/overall JSON。 调用关系必须与 imports 一致：上游只提供数据，下游消费返回值；不要建立 circular import。学生在纸上画箭头，并在箭头写真实 function name 与 return type。

## 12. 数据流解释

frozen checkpoint + gold test -> predicted BIO -> exact sets -> TP/FP/FN -> per-class/overall JSON。 对每一步写下：输入类型、shape/长度、是否修改原对象、输出交给谁。出现 Tensor 时使用 `(batch,sequence,features)` 具体数字；出现字符 span 时使用 `[start,end)`。

## 13. 常见错误

用 token accuracy 单独宣传；边界部分正确算 TP；test 参与调参；只展示成功样例；不注明 synthetic。 排错顺序：确认工作目录和解释器 -> 阅读 traceback -> 打印最小输入/type/shape -> 单独运行当前 Lesson 测试 -> 修复根因 -> 跑本章与全套回归。禁止用删除测试或宽泛 except 制造通过。

## 14. Checkpoint

执行 Lesson 4 命令并保存输出。再口头解释本章新增函数的 parameters、return、调用者和被调用函数。代码测试与口头解释都通过才生成 phase snapshot；只有其中之一不算完成。

## 15. 学生练习

1. 用新的最小输入重复本章函数并预测输出。2. 故意制造一个第 13 节错误，保存 traceback 与修复。3. 给关键函数添加一个边界断言。4. 画跨文件调用图。5. 不看教程重新输入最小代码单元。

## 16. 面试准备

Entity F1 requires exact type and boundaries. The synthetic score is scoped to shared templates; a manual failure demonstrates domain shift.

回答时先说目的，再说输入/输出，最后用实际测试证据和限制收尾；不要背诵库名称。

## 17. 下一阶段预告

Phase 16 把冻结 Predictor 放入 FastAPI，并用真实 HTTP 验收。

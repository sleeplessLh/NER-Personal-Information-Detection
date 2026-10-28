# Phase 16：FastAPI Text API 与真实 HTTP 验收

## 1. 本阶段学习目标

本阶段围绕 `app/main.py` 完成一个可独立验收的功能。为什么现在需要它：比赛要求用户直接输入英文文本；API 把模型能力变成可展示服务。 完成后学生必须能说明输入、输出、参数、返回值、调用者和下一步消费者，而不只是复制代码。

## 2. 本阶段需要掌握的知识

HTTP、JSON、request/response、status code、Pydantic model、endpoint、dependency reuse、Uvicorn。第一次出现时先在 Lesson 1 用普通 Python/具体数值理解，再进入正式文件。

## 3. 从零解释知识点

本阶段坚持“概念 -> 最小代码 -> 局部运行 -> 接入现有项目 -> 回归测试”。关键不是记语法，而是知道数据从哪里来、为什么采用当前类型/shape、错误会在哪一层出现。学生每写一个小单元就保存并运行，不等到整章结束。

正式函数必须回答十二项：名称、目的、parameters、parameter types、return value/type、内部逻辑、调用者、被调用函数、example input/output、common errors。相关答案分布在下面 Lessons、数据流和错误章节。

## 4. 本阶段开始前的项目状态

```text
app/main.py                 [本阶段新增或修改]
tests/                 [本阶段增加/运行对应测试]
tutorial/chapters/phase_16.md [同步更新]
tutorial/code_snapshots/phase_16/ [通过后生成]
```

上一阶段文件保持不变，除非 Lesson 明确指出修改位置。不要提前复制下一阶段代码。

## 5. 本阶段需要使用的工具

打开 VS Code Explorer，定位 `app/main.py`；Terminal -> New Terminal 打开 PowerShell；确认 Working Directory 是项目根目录，prompt 有 `(.venv)`。先执行 `python --version`，再按 Lesson 输入。所有命令默认在根目录、已激活 `.venv`。

### 6. Lesson 16.1：先理解概念和接口

本阶段新概念：HTTP、JSON、request/response、status code、Pydantic model、endpoint、dependency reuse、Uvicorn。先写出一条 sample 的输入类型和预期输出，再打开正式文件。回答：调用者是谁？输入是否可变？失败应 raise 还是返回空值？任何答案不清楚，先阅读第 12/13 节。

### 7. Lesson 16.2：编写第一个最小单元

在 `app/main.py` 对应位置输入：

```python
class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    @field_validator("text")
    def reject_blank_text(cls, value):
        if not value.strip(): raise ValueError("blank")
        return value
```

逐行检查 import、变量 scope、parameter type 和 return。此代码只承担当前职责；不把下一阶段逻辑塞进函数。保存后用 `python -m py_compile app/main.py` 做语法检查。正常无输出、exit code 0。

### 8. Lesson 16.3：连接下一个逻辑单元

在上一段已经通过后，再加入：

```python
@app.post("/api/predict")
def predict(request: TextRequest) -> dict:
    return analyze(request.text)
```

新增代码读取上一单元的返回值，而不是重新计算或使用全局隐藏状态。用具体 sample 手工追踪一遍数据；记录每个 list/dict/Tensor/str 的类型。若涉及 Tensor，打印 shape/dtype 后再接下一层。

### 9. Lesson 16.4：立即运行并记录真实结果

在项目根目录运行：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

本项目真实证据：独立 Uvicorn 进程真实 POST 返回 John/PER、London/LOC、字符位置与 `[PER] lives in [LOC].`。 学生电脑的时间可能不同，但结构、断言和文件数量应一致。命令失败时保留完整 traceback，从最后一行向上找第一个自己的文件行号；修复后重跑同一命令。

## 10. 完整代码回顾

打开 `app/main.py`，从 imports 开始完整阅读。确认本章新增的函数/类与两个代码单元都存在；没有未解释的额外 branch。教材片段用于增量输入，阶段结束时以 snapshot 中完整文件为准。运行 `python -m py_compile app/main.py` 证明至少语法完整。

## 11. 跨文件调用关系

HTTP JSON -> Pydantic TextRequest -> analyze -> Predictor -> redact_text -> dict -> FastAPI JSON response。 调用关系必须与 imports 一致：上游只提供数据，下游消费返回值；不要建立 circular import。学生在纸上画箭头，并在箭头写真实 function name 与 return type。

## 12. 数据流解释

HTTP JSON -> Pydantic TextRequest -> analyze -> Predictor -> redact_text -> dict -> FastAPI JSON response。 对每一步写下：输入类型、shape/长度、是否修改原对象、输出交给谁。出现 Tensor 时使用 `(batch,sequence,features)` 具体数字；出现字符 span 时使用 `[start,end)`。

## 13. 常见错误

空白只靠 min_length；每请求重复加载 checkpoint；在线程环境首次 PyTorch 卡住；把异常都返回 200；端口占用。 排错顺序：确认工作目录和解释器 -> 阅读 traceback -> 打印最小输入/type/shape -> 单独运行当前 Lesson 测试 -> 修复根因 -> 跑本章与全套回归。禁止用删除测试或宽泛 except 制造通过。

## 14. Checkpoint

执行 Lesson 4 命令并保存输出。再口头解释本章新增函数的 parameters、return、调用者和被调用函数。代码测试与口头解释都通过才生成 phase snapshot；只有其中之一不算完成。

## 15. 学生练习

1. 用新的最小输入重复本章函数并预测输出。2. 故意制造一个第 13 节错误，保存 traceback 与修复。3. 给关键函数添加一个边界断言。4. 画跨文件调用图。5. 不看教程重新输入最小代码单元。

## 16. 面试准备

FastAPI validates the request, reuses one trained predictor, and returns typed entities, character offsets and redacted text as JSON.

回答时先说目的，再说输入/输出，最后用实际测试证据和限制收尾；不要背诵库名称。

## 17. 下一阶段预告

Phase 17 增加受限 TXT/PDF 上传和明确错误码。

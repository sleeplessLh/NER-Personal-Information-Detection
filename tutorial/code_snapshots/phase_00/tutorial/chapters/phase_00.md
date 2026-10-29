# Phase 00：项目边界、最终成果与学习方法

## 1. 本阶段学习目标

这一阶段不训练模型。你要先知道“将要造什么、什么算完成、什么绝对不能宣传”。完成后，你应能用自己的话说明：输入是一段英文字符串；输出是 PERSON、LOCATION、ORGANISATION 三类实体、字符位置与脱敏文本；核心预测必须来自本仓库训练的模型，而不是现成 NER API。

为什么先做边界？因为如果一开始把“所有个人资料”误解成 PER/LOC/ORG，后面即使代码全部运行，也会做出错误产品。CoNLL 风格的实体标签不包含电话、邮箱、护照或学号。本项目是教学/比赛原型，不是医院可直接部署的生产系统。

## 2. 本阶段需要掌握的知识

- Project requirement：必须实现的功能约束。
- Acceptance criterion：用什么证据判断功能完成。
- Software correctness 与 ML performance 的区别。
- Repository、source code、checkpoint、dataset、report 的含义。
- 为什么“不编造指标”本身是工程要求。

## 3. 从零解释知识点

Source code 是人编写的程序文本，例如 `src/model.py`。Dataset 是带输入与答案的数据；训练集用来更新参数，验证集用来选模型，测试集只用于最终考试。Checkpoint 是训练后保存的参数和推理所需配置。Metric 是量化表现的数字，但数字必须注明在哪个数据集上得到。

Software correctness 回答“程序是否按规格运行”，例如空输入是否返回错误、PDF 是否能提取文字。ML performance 回答“预测是否正确”，例如 Person recall。`pytest` 全通过不代表模型不会漏人名；反过来，F1 很高也不代表文件上传安全。

本项目的真实边界：Embedding + casing features + BiLSTM + Linear，从随机权重训练；没有现成 NER pipeline。它支持文本、TXT、文字层 PDF、网页和 redaction。扫描 PDF 没有 OCR。合成模板测试 F1 很高，但手动挑战句确实出现漏检，因此必须人工复核。

## 4. 本阶段开始前的项目状态

学生开始时只需要一个空文件夹。正式完成版本会逐步出现：

```text
Intern-MachineLearning/
  learning/                 # 前置练习
  src/                      # 模型与数据代码
  app/                      # FastAPI 和网页
  tests/                    # 自动化测试
  data/                     # 数据集
  models/                   # checkpoint
  reports/                  # 训练与评估证据
  tutorial/                 # 本教材源文件与快照
```

本阶段不要求这些目录已经存在。下一阶段才实际创建第一个文件。

## 5. 本阶段需要使用的工具

先准备纸笔或文本编辑器即可。若你已经打开 VS Code：点击左上角 Explorer 图标，观察当前文件夹；不要随意运行不理解的命令。本阶段命令只用于读取，不会训练或修改模型。

### 6. Lesson 00.1：把需求改写成输入与输出

输入示例：

```text
Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.
```

目标实体是 Sarah/PER、Microsoft/ORG、Kuala Lumpur/LOC。脱敏目标是：

```text
[PER] works at [ORG] in [LOC].
```

这里的方括号不是模型输入，而是应用层根据模型预测的字符范围生成的结果。模型先预测 BIO 标签，redaction 后处理才替换文字。

在纸上完成练习：给句子 `Ali studies at Universiti Malaya.` 标出实体。不要用关键词表；你只是先理解预期输出。

实际验收：最终模型对这类合成分布样例可返回实体，但我们不会因为一个样例正确就宣称模型性能优秀。

### 7. Lesson 00.2：建立证据层级

打开项目根目录的 `MODEL_ACCEPTANCE_REPORT.md`。先找 Software Tests，再找 Machine Learning Evaluation，最后找 Manual Demonstrations。三个区域不可合并。

在项目根目录 PowerShell 执行：

```powershell
Get-Content MODEL_ACCEPTANCE_REPORT.md -TotalCount 40
```

`Get-Content` 读取文本；`-TotalCount 40` 只显示前 40 行。它不会修改文件。实际项目输出开头包含执行日期、平台和 requirement checklist。

若提示找不到文件：先执行 `Get-Location`，确认 Working Directory 是项目根目录。若你从空目录学习，本文件要到 Phase 20 才创建，因此本练习标记为“教师演示，不适用于学生空目录”，不是错误。

### 8. Lesson 00.3：识别禁止的捷径

以下做法不合格：调用 OpenAI/Gemini/Google Cloud 识别实体；直接加载 spaCy 或 Hugging Face 已训练 NER pipeline；查看 test label 后反复修改模型；只展示伪造运行结果。

允许使用 PyTorch、NumPy、FastAPI、pypdf 等辅助库，因为分类权重仍由自己的训练产生。正则表达式可以负责 tokenization，但不能硬编码 `Microsoft -> ORG` 作为核心预测。

运行只读检查：

```powershell
rg -n "spacy|pipeline\(|openai|gemini" src app
```

`rg` 是快速文本搜索工具；`-n` 显示行号。最终验收代码没有这些 NER 调用，因此正常结果可能为空。命令找不到 `rg` 时可使用 VS Code 的 Ctrl+Shift+F 搜索。

### 9. Lesson 00.4：定义完成条件

本教程只有同时具备以下证据才完成：数据校验、真实训练日志、冻结测试指标、checkpoint 重载、字符 span、redaction、Malaysian 独立测试、TXT/PDF、真实 HTTP、自动化测试、README、验收报告、教学快照与 PDF 全页检查。

公开 GitHub 需要仓库所有者授权。若没有 URL，只能写“发布准备完成，尚未发布”，不能写 PASS。

## 10. 完整代码回顾

本阶段没有业务代码，这是唯一合理的不适用项：目标是建立需求与证据边界。可执行内容是只读检查命令。没有创建模型文件，因此不存在可展示的 Python 完整代码。下一阶段会创建第一个 Python 文件。

## 11. 跨文件调用关系

当前没有运行时调用。未来数据流是：`app/main.py` 接收文本 -> `src/predict.py` 分词并加载 checkpoint -> `src/model.py` 计算标签 -> `src/predict.py` 合并实体 -> `src/redact.py` 替换字符区间 -> API 返回 JSON。

验收证据流是：`reports/*.json` + `pytest` + 手测结果 -> `MODEL_ACCEPTANCE_REPORT.md` -> 教程 Phase 20/21。

## 12. 数据流解释

原始输入类型是 Python `str`。Tokenizer 产生 `list[str]` 和字符区间。Vocabulary 把 token 转成 `list[int]`。Dataset 把它变成 `torch.Tensor`。模型输出 logits tensor。Argmax 产生标签 ID，再映射到 BIO 字符串。实体抽取器产生 `list[dict]`，最后 redaction 返回新的 `str`。

这一阶段只认识流程名称，不要求掌握 Tensor；Phase 07 会从数字和 shape 开始教学。

## 13. 常见错误

1. 把 NER 当成所有 PII：修复方法是列出不支持的电话、邮箱、ID、地址。
2. 把合成 test F1=1.0 当生产表现：查看手动失败案例。
3. 把 PDF 提取器当 NER：pypdf 只提供文本，分类仍由模型完成。
4. 把测试通过当公开 GitHub：发布是独立外部动作。
5. 一开始复制最终代码：你会失去增量学习和错误定位能力。

## 14. Checkpoint

口头回答并记录：三种实体是什么？核心预测由谁完成？Software correctness 与 ML performance 有何不同？为什么扫描 PDF 不支持？为什么高风险场景仍需人工？五题全部能回答才通过。

教师验收命令（最终仓库）：

```powershell
uv run python -m pytest -q
```

本轮最近一次真实结果是 `22 passed`。这只是已有最终工程的基线，不是学生 Phase 00 应自行得到的输出。

## 15. 学生练习

1. 写三个句子，各包含 PER、LOC、ORG。
2. 列出五种本模型无法检测的敏感标识。
3. 用两句话说明为什么不能用 test set 选最佳 epoch。
4. 解释“文件可以读取”和“实体预测正确”为何是两种证据。

## 16. 面试准备

简单英语："I built an educational NER prototype that detects people, locations and organisations. The core predictions come from a model trained in this repository. Software tests and machine-learning metrics are reported separately. The system is not a production PII solution and still requires human review."

## 17. 下一阶段预告

Phase 01 会从真正的 Windows 11 操作开始：检查 Python、安装 VS Code、创建 `.venv`、选择解释器、安装依赖并运行 `learning/hello_python.py`。完成后，你才拥有可靠的开发环境。

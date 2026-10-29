# NER 项目式机器学习编程教材

## Divide and Conquer 学生实战版

学习承诺：每学一点，就实现一点；每实现一点，就立即验证一点。参考项目已经先完成训练与验收，但你在本教材中会从空文件夹开始，依次构建同一个系统。每个阶段都遵循 Concept -> Implementation -> Explanation -> Execution -> Verification -> Integration。

实际验证环境：Windows 11 10.0.26200、CPython 3.12.15、PyTorch 2.9.0+cpu、uv 0.13.1。CUDA、Linux、macOS 没有在本次项目中验证。数据为透明合成模板语料；完美合成测试分数不能解释为生产性能。

# 阅读方法与代码演进规则

每次看到“新增位置”，先打开指定文件，定位所述 class/function，再粘贴增量代码。标记“保持不变”的部分不要删除。关键阶段会给出当前完整版本供核对；最终 Appendix 会自动读取验收源码。Import 是把另一个模块中的名字带入当前文件；Object Creation 是调用 class 创建对象；Function Call 是执行对象的方法；Return Value 是被调用代码交回的数据；Data Transfer 是 Tensor/字典在模块之间移动。它们不是同一概念。

Code Evolution Tracking：`preprocessing.py` 从 Tokenization -> Vocabulary -> features；`dataset.py` 从单样本 -> Tensor -> padding collator；`model.py` 从 nn.Module 外壳 -> Embedding -> BiLSTM -> Linear -> forward；`train.py` 从单 Batch -> Epoch -> Validation -> checkpoint；`predict.py` 从加载 -> BIO -> span；`app/main.py` 从文本 API -> 页面 -> TXT/PDF。

# Phase 0 项目目标与比赛边界

## 目标与位置

实现由自己训练的 PERSON/LOCATION/ORGANISATION NER，而不是关键词或第三方 API。完成后应能解释 Raw Text -> BIO -> Entity -> Redaction -> Web 的全链路。

## 必要理论

NER 是 sequence labeling。核心必须是可训练模型；正则只可支持 Tokenization。合成数据只能证明教学管线，不证明真实场景泛化。

## 操作、执行与验证

使用工具：VS Code。操作位置：项目根目录。新建 `PROJECT_PROGRESS.md`，写下模型、数据、API、测试、PDF 五个未完成框。此阶段无模型代码。验收：你能口头说明为什么现成 API 不符合 Own Trained Model。

## 集成、总结与 Checkpoint

新增文件：进度表。当前功能：只有可审计目标。下一阶段：环境。问题：规则能否作为核心预测？答案：不能，因为它不通过 Loss 和 Gradient 学习。

# Phase 1 Windows 11 开发环境

## 目标与必要理论

建立隔离、锁定、可复现的 Python 环境。`.venv` 防止不同项目依赖互相污染；`uv.lock` 固定解析结果。

## 操作指导

安装 VS Code 与 Microsoft Python Extension。打开项目根目录，在 Terminal -> New Terminal 打开 PowerShell，执行 `uv sync --all-groups`；Ctrl+Shift+P -> Python: Select Interpreter -> `.venv\Scripts\python.exe`。

## 执行与验证

执行 `uv run python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"`。本机验收输出为 `2.9.0+cpu` 和 `False`。若 ModuleNotFoundError，检查终端当前目录和 interpreter。

## 总结与 Checkpoint

新增 `.venv`、`uv.lock`；尚无 NER。问题：为什么不能只写 requirements 而不创建环境？答案：清单描述依赖，环境才实际隔离并安装依赖。

# Phase 2 第一个 Tensor 程序

## 目标与理论

Tensor 是有 Shape 的多维数字容器，也是 PyTorch 的基本数据结构。本阶段不提前学习训练。

## 操作与增量代码

在项目根目录新建 `learning/phase02_tensor.py`：

```python
import torch  # 导入 PyTorch，提供 Tensor 运算

# 两个句子，每个句子五个 Token ID
token_ids = torch.tensor([[2, 3, 4, 0, 0], [5, 6, 7, 8, 9]])
print(token_ids)
print(token_ids.shape)
```

## 解释、执行与验证

`torch.tensor` 接收嵌套 list；dtype 会推断为整数。执行 `uv run python learning/phase02_tensor.py`。预期 `torch.Size([2, 5])`：2 是 Batch Size，5 是 Sequence Length，0 暂作 Padding。

## 集成、总结与 Checkpoint

这是局部实验，尚未被 src 调用。问题：为何字符串不能直接进入 Embedding？答案：Embedding 用整数 ID 作为查表索引。

# Phase 3 NER 与 BIO 手工实验

## 目标与理论

理解 Sentence、Token、Entity、Label 和 BIO，不写神经网络。B 是实体开始，I 是同一实体延续，O 是外部。

## 操作与增量代码

新建 `learning/phase03_bio.py`，手写：

```python
tokens = ["Ali", "studies", "at", "Universiti", "Malaya"]
labels = ["B-PER", "O", "O", "B-ORG", "I-ORG"]

for token, label in zip(tokens, labels, strict=True):
    print(f"{token:12} {label}")
```

## 执行、验证与总结

执行 `uv run python learning/phase03_bio.py`。确认两 list 等长且 Universiti/Malaya 是一个实体。问题：为什么 Malaya 不是 B-ORG？答案：它延续同一个组织 span。

# Phase 4 生成、读取和检查 Dataset

## 目标与位置

创建 `src/generate_data.py`，输出 `data/processed/*.jsonl`。先只实现一个 `_annotate` 和 JSONL writer，再加入独立实体池与 split 检查。

## 必要理论

Training 更新参数；Validation 选模型；Test 只做最终评估。相同规范化句子不能跨 split。真实私人资料不得进入教学数据。

## 操作与代码演进

Version 1：写一条 `{tokens, labels, text}` JSON。Version 2：按模板循环生成。Version 3：train/validation/test 使用不同实体 pool。Version 4：加入：

```python
texts = {row["text"].lower() for row in rows}
overlap = all_texts & texts
if overlap:
    raise RuntimeError(f"Sentence leakage into {split}")
all_texts |= texts
```

新增在 `main()` 每个 split 写文件之前；其他生成逻辑保持不变。

## 执行与验证

执行 `uv run python -m src.generate_data`。验收：2400/300/300 行；唯一句子 1613/184/215；跨 split overlap=0。失败时先修正数据，不能跳过。

## 总结与 Checkpoint

新增 processed JSONL 与 Malaysian challenge。下一阶段把字符串变 ID。问题：能否查看 test labels 后改模板？答案：不能，那会把 Test 变成 Validation。

# Phase 5 Preprocessing

## 目标与理论

在 `src/preprocessing.py` 依次加入 Tokenization、Vocabulary、Unknown、casing features 和 BIO 校验。

## 增量实现

Lesson 5.1 新增 `tokenize(text)`；Lesson 5.2 新增 `build_vocabulary` 并固定 `<PAD>=0,<UNK>=1`；Lesson 5.3 新增 `tokens_to_ids`；Lesson 5.4 新增四个大小写特征；Lesson 5.5 新增 `validate_bio`。

```python
def tokens_to_ids(tokens, vocabulary):
    unknown_id = vocabulary["<UNK>"]  # 未见词统一使用 ID 1
    return [vocabulary.get(token.lower(), unknown_id) for token in tokens]
```

## 跨文件关系与验证

此时 `generate_data.py` import `validate_bio`；未来 `dataset.py` import ID/features。执行 `uv run pytest tests/test_preprocessing.py -q`。验收 Tokenization、unknown、feature shape、非法 I-tag。问题：为什么原 Token 不直接变小写？答案：显示和大小写特征需要原形式。

# Phase 6 PyTorch Dataset 与 DataLoader

## 目标与理论

`Dataset.__getitem__` 返回单句 Tensor；`DataLoader` 组成 Batch；`collate_batch` 负责 Padding 与 mask。

## 代码演进

Version 1：`load_jsonl`。Version 2：`NERDataset.__len__/__getitem__`。Version 3：`collate_batch`。Version 4：只在训练集加入 word dropout。

```python
# input_ids/labels/mask: (batch_size, max_length)
input_ids = torch.zeros((batch_size, max_length), dtype=torch.long)
features = torch.zeros((batch_size, max_length, 4), dtype=torch.float32)
```

## 执行与验证

在 Debugger 查看一个 Batch。若 batch=2、最长句=7，则 IDs `(2,7)`，features `(2,7,4)`。Padding mask 为 False。问题：为什么不能把所有语料永久 Padding 到全局最长？答案：浪费计算与内存。

# Phase 7 Neural Network 分层搭建

## 目标与理论

只创建层，暂不连接 forward。打开 `src/model.py`。

## Lesson 7.1 到 7.4

Version 1：class 和 `super().__init__()`；Version 2：`nn.Embedding`；Version 3：feature projection 与 BiLSTM；Version 4：Dropout 与 Linear。

```python
class BiLSTMNER(nn.Module):
    def __init__(self, vocab_size, num_labels, embedding_dim=64, hidden_dim=96, dropout=0.25):
        super().__init__()  # 注册所有子层与可训练参数
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.feature_projection = nn.Linear(4, 8)
        self.lstm = nn.LSTM(embedding_dim + 8, hidden_dim,
                            batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim * 2, num_labels)
```

## 外部解释与验证

Embedding 是 vocab_size x 64 查找表；BiLSTM 每方向 96，拼接后 192；Linear 把 192 映射到 8 labels。此阶段实例可创建，但没有 forward，不能预测。局部验证 `model = BiLSTMNER(100,8); print(sum(p.numel() for p in model.parameters()))`。

## Checkpoint

为什么乘 2？答案：双向输出拼接。num_labels 错会怎样？答案：logits 最后一维与 Label Mapping/Loss 不一致。

# Phase 8 Forward Pass

## 目标与增量修改

在 `BiLSTMNER` class 内、`__init__` 后新增 `forward`；原 layers 保持不变。

```python
def forward(self, input_ids, features):
    embedded = self.embedding(input_ids)                 # (B,L,64)
    projected = torch.relu(self.feature_projection(features))  # (B,L,8)
    combined = torch.cat([embedded, projected], dim=-1) # (B,L,72)
    encoded, _ = self.lstm(combined)                    # (B,L,192)
    return self.classifier(self.dropout(encoded))       # (B,L,8)
```

## 调用流程与执行

test_model.py -> create `BiLSTMNER` -> call `model(ids,features)` -> nn.Module calls `forward` -> return logits -> test checks Shape。执行 `uv run pytest tests/test_model.py -q`；预期 `(2,3,8)` 且 gradient 非 None。

## 总结与 Checkpoint

模型现在能前向计算，但尚未学习。问题：为什么不在 forward 里 Softmax？答案：CrossEntropyLoss 内部已经处理。

# Phase 9 Training：一个 Batch 到一个 Epoch

## 目标与理论

创建 `src/train.py`。Loss 衡量预测错误；Backpropagation 计算 Gradient；Adam 更新参数。

## 逐步实现

Version 1：加载一个 Batch 和 model。Version 2：加入 `CrossEntropyLoss(ignore_index=PAD)`。Version 3：严格按下面顺序：

```python
optimizer.zero_grad()          # 清空上个 Batch 的 Gradient
logits = model(input_ids, features)
loss = criterion(logits.reshape(-1, logits.shape[-1]), labels.reshape(-1))
loss.backward()                # 反向传播
torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
optimizer.step()               # 真正更新参数
```

Version 4：外层遍历 DataLoader，形成 `run_epoch`。执行一个 epoch 时检查 loss 不是 NaN、classifier weight 前后不同。

## 执行与验收

执行 `uv run python -m src.train --epochs 1 --batch-size 64`。必须完成 1 epoch、打印 loss、生成可加载 checkpoint。问题：删除 zero_grad 会怎样？答案：梯度意外跨 Batch 累积。

# Phase 10 Validation 与过拟合诊断

## 目标与实现

调用相同 `run_epoch`，但 optimizer=None、`model.train(False)`、外部 `torch.no_grad()`。Validation 不执行 backward/step。

## 实验事实

早期基线 validation F1=0.1976：模型背记训练实体。加入 entity word dropout 后 0.6494；增加多词地点后 0.8681；再加入 ordinary word dropout 后曾达到 0.9685。最终聚焦学生隐私场景，加入 Malaysian train/validation、跨来源互斥实体池和学生报告模板并重训 16 epochs，最佳 epoch 16 validation F1=0.9192。理论跟随失败出现：Overfitting 是 train 极好、validation 差；合成模板上的高 validation 仍不等于真实泛化。

## 验收与 Checkpoint

每 epoch 必须记录 train loss、validation loss/precision/recall/F1、duration。问题：为什么不能用 Test 选 epoch？答案：会泄漏最终考试信息。

# Phase 11 Model Saving 与重新加载

## 目标与实现

只保存 weight 不够；推理还需要 vocabulary、labels、config、preprocessing、seed。Validation F1 改善时 `torch.save({...}, models/best_model.pt)`。

## 跨文件调用

train.py 创建 model -> 保存 state_dict；predict.py 读取 config -> 创建相同 model -> load_state_dict -> eval。执行 `uv run pytest tests/test_prediction.py::test_saved_model_reloads_and_predicts_required_types -q`。

## 验收与 Checkpoint

新 Python 进程可加载；SHA-256 为 `146B...DCC3`。问题：为何 model.eval 必须调用？答案：关闭 Dropout 等训练行为。

# Phase 12 Inference 与实体抽取

## 目标与实现

在 `src/predict.py` 先实现 `predict_tokens`，再实现 `extract_entities`，最后由 `predict(text)` 串联。

```text
Raw text -> tokenize -> IDs/features -> model -> argmax tags
         -> extract_entities -> list[dict]
```

argmax 输出 label ID；使用 checkpoint labels 映射回字符串。B 开始 span，I 延续，O 关闭 span。执行 prediction tests；验收新文本、初始非法 I 的安全处理、无实体句。

## Checkpoint

`torch.no_grad` 的作用？答案：推理不构建 autograd graph，减少内存与开销。

# Phase 13 Entity-level Evaluation

## 目标与理论

在 `src/metrics.py` 实现 BIO -> spans 与 TP/FP/FN。Precision 看误报，Recall 看漏报，F1 平衡二者。大量 O 会令 Token Accuracy 虚高，所以采用 exact span entity F1。

## 执行与验证

`src/evaluate.py` import `Predictor` 和 `entity_metrics`，读取 test，预测但不更新权重。执行 `uv run python -m src.evaluate`。真实合成结果 Overall/PER/LOC/ORG F1 均 1.0000；必须同时陈述模板分布限制。

# Phase 14 Automatic Redaction

## 目标与实现

创建 `src/redact.py`。早期版本按 Token index 重建字符串；最终验收版改为 tokenizer 保存原始字符 `[start,end)`，然后从右向左替换实体。这样后方替换不会让前方 offset 失效，并能逐字符保留实体外的双空格、换行和标点。

## 执行、验证与集成

执行 `uv run pytest tests/test_redaction.py -q`。验收多词实体只替换一次、重复实体各替换一次。predict 的 entities 是输入，redact 不重新判断类别。

# Phase 15 Malaysian Dataset

## 目标与伦理

使用公开机构/地点和合成人名，不把虚构内容说成真实采集。最终生成 `data/malaysian/train.jsonl` 160 条、`validation.jsonl` 40 条、`test.jsonl` 60 条。实体池与完整句子跨 split 隔离；训练只合入本地 train/validation，本地 test 保持冻结。

## 标注质量与验收

规则：完整官方机构名是 ORG；城市/州为 LOC；合成人名为 PER。真实扩展应由两人独立标注、解决分歧、按文档来源切分。当前验收只证明脚本可读和模型可运行，不声称代表马来西亚人口分布。

# Phase 16 FastAPI Backend

## 目标与增量实现

创建 `app/main.py`。Version 1：FastAPI app；Version 2：TextRequest；Version 3：lazy Predictor；Version 4：POST `/api/predict`。

```python
@app.post("/api/predict")
def predict(request: TextRequest) -> dict:
    return analyze(request.text)
```

Pydantic 在函数前校验 JSON；空文本 422。执行 `uv run python -m uvicorn app.main:app --reload`，浏览 `/docs` 并 POST。调用链：HTTP -> endpoint -> analyze -> Predictor -> redaction -> dict -> JSON。

# Phase 17 Frontend

## 目标与实现

在 GET `/` 返回的 HTML 中逐步加入 textarea、button、pre，再添加 `fetch('/api/predict')`。JavaScript 只传输数据，不在浏览器执行模型。

## 验收

打开 `http://127.0.0.1:8000`，输入 Sarah 样例，页面应显示 3 entities 与 `[PER] works at [ORG] in [LOC].`。错误时用浏览器 DevTools Network 查看 status 和 response。

# Phase 18 TXT/PDF File Upload

## 目标与增量修改

先在 HTML 添加 file input，再在后端添加 POST `/api/upload`。TXT decode UTF-8；PDF `PdfReader(BytesIO(content))` 提取 text layer；随后调用同一个 `analyze`。

## 验收与边界

测试动态生成的文字 PDF 与 TXT；不支持扩展名 415、空/扫描 PDF 400。pypdf 只提取文字，NER 仍由自己的模型完成。扫描 PDF OCR 未实现。

# Phase 19 自动化测试与错误修复

## 目标与测试金字塔

按文件运行 preprocessing、model、prediction、redaction、api tests，再运行全套。执行 `uv run python -m pytest -q --cov=src --cov=app`。

## 真实验收

最终实测 `22 passed in 16.88s`；coverage 47%。低覆盖主要来自没有在 pytest 中重复跑完整训练/生成 CLI，但这两个 CLI 已独立真实执行。进程内 ASGI transport 在 Windows 沙箱与 PyTorch 线程组合下曾卡住，因此自动化测试直接验证 endpoint 函数，另用独立 Uvicorn 进程完成真实 HTTP POST，二者分开记录。

## Checkpoint

人工样例通过是否等于模型性能通过？答案：不等；还需独立 test 和指标。

# Phase 20 完整 Acceptance

## 目标与操作

依次验证 checkpoint 新进程加载、五条手动样例、无实体、多/重复实体、标点、TXT、PDF、API、服务重启。两次隐藏 Uvicorn 进程在 8765/8766 均真实返回 3 entities。

## 结论边界

Level A 全部通过；Level B 合成 test F1 与 PERSON recall 均 1.0。生产泛化、OCR、真实用户试读未通过/未声称。任何未测试项必须写 NOT CLAIMED。

# Phase 21 README、Git 与 GitHub 准备

## 目标与操作

README 给陌生人提供 install/train/evaluate/run/test。`.gitignore` 排除环境和临时渲染。执行 `git status`、`git diff --check`，检查 secret、私人数据和 checkpoint 大小后再 commit。

## 验收与边界

本任务没有授权公开发布，所以没有 push。问题：为什么 PDF 生成器自动读取源码？答案：降低手工复制造成代码与验收版本不一致的风险。

# Phase 22 项目演示与技术面试

## 5-10 分钟演示结构

Problem -> Privacy Motivation -> BIO Dataset -> Embedding/BiLSTM -> Training Failures -> Validation/Test -> Demo -> Limitations -> Improvements。最有价值的是解释从 0.1976 到 0.9685 validation F1 的诊断过程，而不是背诵完美测试分数。

## 40 道核心问题与中英回答

1 NER？中文：为 Token 分配 BIO 并恢复有类型 span。English: NER assigns BIO tags and reconstructs typed spans.
2 为什么 BiLSTM？中文：每个 Token 同时使用左右上下文。English: It encodes both left and right context.
3 RNN/LSTM？中文：LSTM gates 缓解长距离梯度消失。English: LSTM gates mitigate vanishing gradients.
4 Embedding？中文：可训练 ID 查找表。English: A trainable lookup table maps IDs to dense vectors.
5 BIO？中文：B/I/O 表示开始、内部、外部。English: BIO preserves multi-token boundaries.
6 如何学习？中文：Cross Entropy、Backprop、Adam。English: It minimizes cross-entropy with backpropagation and Adam.
7 Gradient？中文：Loss 对参数的局部变化率。English: A gradient measures local loss sensitivity.
8 Validation？中文：选 checkpoint 而不污染 test。English: Validation selects the checkpoint without test leakage.
9 Overfitting？中文：训练好、未见数据差。English: Training performance improves while generalization fails.
10 Recall 为什么重要？中文：漏报可能暴露隐私。English: False negatives can expose personal data.
11 未见姓名？中文：UNK、大小写、上下文。English: UNK, casing, and context support unseen names.
12 Unknown？中文：映射 ID 1。English: It maps to the trained UNK embedding.
13 为什么是 ML？中文：143,536 个参数由 Gradient 更新。English: Trainable parameters are optimized from labels.
14 是否自己训练？中文：是，自定义 nn.Module 从随机权重训练 16 epochs。English: Yes, I defined and trained the architecture from random weights.
15 最大限制？中文：合成模板与 domain shift。English: Synthetic templates do not prove real-world generalization.
16 Softmax？中文：Logits 归一化；Loss 内置。English: Cross-entropy applies log-softmax internally.
17 Logit？中文：未归一化类别分数。English: An unnormalized class score.
18 Cross Entropy？中文：惩罚 gold 类分数低。English: It penalizes low gold-label likelihood.
19 Optimizer？中文：根据 Gradient 更新参数。English: It updates parameters from gradients.
20 zero_grad？中文：清除默认累积梯度。English: PyTorch gradients accumulate unless cleared.
21 Batch？中文：一次并行处理多句。English: A batch processes multiple sentences together.
22 Padding？中文：补齐长度且从 Loss 排除。English: Padding aligns lengths and is ignored by loss.
23 Mask？中文：标记真实 Token。English: A mask separates real tokens from padding.
24 Entity F1？中文：边界和类型完全正确。English: It requires exact span and type matches.
25 Token accuracy 缺点？中文：O 类会虚高。English: The dominant O class can inflate it.
26 双向维度？中文：96+96=192。English: Two 96-dimensional directions concatenate.
27 forward 输入？中文：IDs `(B,L)` 与 features `(B,L,4)`。English: IDs and four casing features.
28 forward 输出？中文：logits `(B,L,8)`。English: Eight label logits per token.
29 eval？中文：关闭 Dropout。English: Eval mode disables dropout.
30 no_grad？中文：不建计算图。English: It avoids autograd graph construction.
31 checkpoint 内容？中文：权重、词表、标签、配置、seed。English: Weights plus all inference metadata.
32 Leakage？中文：测试信息影响训练。English: Test information improperly influences training.
33 完美分数可信吗？中文：只限模板分布。English: It is scoped to the synthetic template distribution.
34 为什么无 CRF？中文：简单 Linear 已满足教学目标。English: Simplicity matched the validated teaching scope.
35 CRF 改进？中文：学习标签转移约束。English: It can model valid tag transitions.
36 Redaction？中文：按预测 span 跳跃替换。English: It replaces predicted token spans.
37 PDF 谁做 NER？中文：pypdf 取字，自己模型预测。English: pypdf extracts text; my model performs NER.
38 扫描 PDF？中文：需要 OCR，当前未实现。English: OCR is outside the current scope.
39 API 错误？中文：422/400/415 清晰返回。English: Validation and file errors use explicit status codes.
40 下一步？中文：真实盲测、character encoder、可能 CRF。English: Real blind data, character features, then possibly a CRF.

# Phase 23 将 Malaysian 数据真正加入训练

## A-M 教学卡

A Learning Objectives：让本地 train/validation 进入训练，但 test 永远不进入。B Prerequisite：理解三个 split。C Concept：`list.extend` 合并样本，词表只能从最终 training rows 建立。D Structure：修改 `src/train.py`，保持 `model.py` 不变。E Tools：在 VS Code 打开 `src/train.py`，PowerShell 位于项目根目录。

F Incremental Code：在读取主数据之后加入：

```python
local_train_rows = load_jsonl(MALAYSIAN_DIR / "train.jsonl")
local_validation_rows = load_jsonl(MALAYSIAN_DIR / "validation.jsonl")
train_rows.extend(local_train_rows)
validation_rows.extend(local_validation_rows)
```

G Explanation：`extend` 逐条加入 dict；返回值是 `None`，不要写成 `train_rows = train_rows.extend(...)`。H Relationships：local JSONL -> `load_jsonl` -> `NERDataset` -> `DataLoader` -> model。I Run：`uv run python -m src.train --epochs 16 --batch-size 64 --learning-rate 0.003`。J Expected：16 行 JSON epoch 日志和 best checkpoint。K Errors：缺文件先运行 generator；label 不合法先修数据。L Checkpoint：checkpoint 的 `dataset_counts` 必须显示 160/40。M Interview："I merged only the Malaysian training and validation splits. The local test split remained unseen."

# Phase 24 双测试集冻结评估

## A-M 教学卡

A 目标：一般 test 与 Malaysian test 分开报告。B 前置：Precision/Recall/F1 与 `model.eval()`。C 概念：冻结评估不能创建 optimizer。D 文件：修改 `src/evaluate.py`，新增 `reports/malaysian_test_metrics.json`。E 工具：PowerShell。

F Incremental Code：

```python
local_rows = load_jsonl(MALAYSIAN_DIR / "test.jsonl")
local_metrics = entity_metrics(
    [row["labels"] for row in local_rows],
    [predictor.predict_tokens(row["tokens"]) for row in local_rows],
)
save_json({"sentences": len(local_rows), "metrics": local_metrics}, output_path)
```

G 解释：两个 list comprehension 必须保持相同行顺序；`predict_tokens` 不读取 gold。H 关系：checkpoint + local test -> predictor -> metrics -> JSON。I 命令：`uv run python -m src.evaluate`。J 预期：两个报告。K 错误：若 test 被训练脚本读取，立即停止并修复。L 验收：本地报告 `sentences=60`。M Interview："I evaluated the frozen checkpoint separately on an unseen Malaysian split."

# Phase 25 原始字符 Offset 与可靠 Redaction

## A-M 教学卡

A 目标：返回 `start/end` 并保留原文格式。B 前置：Python slice 与 half-open interval。C 概念：`[start,end)` 可直接执行 `text[start:end]`。D 文件：修改 preprocessing/predict/redact。E 工具：单元测试。

F Incremental Code：

```python
matches = list(TOKEN_PATTERN.finditer(text))
tokens = [m.group(0) for m in matches]
spans = [m.span() for m in matches]

for entity in sorted(entities, key=lambda x: x["start"], reverse=True):
    text = text[:entity["start"]] + f"[{entity['type']}]" + text[entity["end"]:]
```

G 解释：从右向左可防止替换后字符串长度变化破坏尚未使用的左侧 offset。H 关系：regex match -> token span -> entity span -> API/redaction。I 命令：`uv run pytest tests/test_prediction.py tests/test_redaction.py -q`。J 预期：双空格和换行保留。K 错误：不要把 end 当 inclusive。L 验收：每个 entity 都满足 `original[start:end] == entity.text`。M Interview："I use half-open character spans and redact from right to left."

# Phase 26 文件上传安全边界

## A-M 教学卡

A 目标：限制类型、大小、编码和空内容。B 前置：bytes/string、HTTP status。C 概念：不要先无限读取大型文件。D 文件：`app/main.py` 与 API tests。E 工具：ReportLab 生成测试 PDF。

F Incremental Code：

```python
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
content = await file.read(MAX_UPLOAD_BYTES + 1)
if len(content) > MAX_UPLOAD_BYTES:
    raise HTTPException(status_code=413, detail="File exceeds the 5 MB limit")
```

G 解释：多读 1 byte 可区分“刚好上限”和“超过上限”。H 关系：UploadFile -> bytes -> decoder/PdfReader -> analyze。I 命令：`uv run pytest tests/test_api.py -q`。J 预期：TXT/PDF 成功，CSV 415，超大 413。K 错误：扫描 PDF 没文字层会 400，不等于模型失败。L 验收：任何文件最终仍调用自己的 Predictor。M Interview："File parsing is auxiliary; NER always uses my trained model."

# Phase 27 Windows CPU 线程问题调试

## A-M 教学卡

A 目标：识别“模型错误”和“运行时卡死”的差别。B 前置：process/thread。C 概念：OpenMP 线程过度订阅可令小模型首次 forward 异常慢。D 文件：`src/predict.py`、README。E 环境：PowerShell。

F Incremental Code：

```python
torch.set_num_threads(1)
# PowerShell 启动前也可设置：
# $env:OMP_NUM_THREADS="1"
# $env:MKL_NUM_THREADS="1"
```

G 解释：这只影响 CPU 调度，不改变 checkpoint 数值。H 关系：Predictor 初始化 -> PyTorch runtime -> forward。I 验证：先直接 Predictor，再真实 Uvicorn HTTP。J 预期：数秒内返回。K 错误：不要因测试线程门户卡住就删掉 API 测试；改为分层验证。L 验收：22 tests + 独立 HTTP。M Interview："I separated an ASGI test-harness issue from model correctness and verified a real server process."

# Phase 28 性能优化与失败案例分析

## A-M 教学卡

A 目标：解释高分为何仍不够。B 前置：distribution shift、overfitting。C 概念：实体不重复不代表模板不重复。D 文件：reports 与 acceptance。E 工具：手动 challenge。

F 增量实验代码：

```python
texts = [
    "Farah works at Telekom Malaysia in Cyberjaya.",
    "Dr. Evelyn Carter emailed the research team from Oxford.",
]
for text in texts:
    print(predictor.predict(text))
```

G 解释：第二句漏掉姓名并误标 Oxford，是真实负证据。H 关系：manual samples 不用于更新权重，只用于风险分析。I 命令：运行上述脚本。J 预期：保留成功与失败。K 错误：不要只展示 cherry-picked 样例。L 验收：报告中包含至少一个失败。M Interview："The 1.0 synthetic F1 is not real-world performance because templates are shared."

# Phase 29 README 与公开 GitHub 准备

## A-M 教学卡

A 目标：让陌生 Windows 学生可重现。B 前置：Git。C 概念：源码可公开不等于已经公开。D 文件：README/.gitignore。E 工具：GitHub 网页或 gh CLI（需用户授权）。F 增量：补齐 Introduction/Installation/Dependencies/Dataset/Training/Running/Testing/Architecture/Results/Limitations。G 解释：不要提交 `.venv` 与 pytest temp；checkpoint 0.6 MB 可提交，但大模型通常用 Releases/LFS。H 关系：README 指向所有 CLI。I 命令：`git status`、`git diff --check`。J 预期：无 secret、无 TODO。K 错误：占位 URL 必须发布后替换。L 验收：本地已准备；本任务没有 GitHub 权限，状态明确为未发布。M Interview："The repository is publication-ready, but I do not claim it is public until it is pushed."

# Phase 30 完整验收报告

## A-M 教学卡

A 目标：把软件测试、ML 指标、手测分开。B 前置：evidence。C 概念：pytest PASS 不等于模型性能好。D 文件：`MODEL_ACCEPTANCE_REPORT.md`。E 工具：pytest/evaluate/Uvicorn。F 增量：填写命令、时间、参数数、TP/FP/FN、失败案例。G 解释：所有数值必须来自 JSON 或终端。H 关系：reports + tests + manual -> acceptance。I 命令：依次 generate/train/evaluate/pytest/server。J 预期：Requirement checklist 有 PASS/NOT COMPLETED/NOT CLAIMED。K 错误：不可把 GitHub 未发布写成 PASS。L 验收：19 类测试覆盖、真实 HTTP、限制齐全。M Interview："I separate functional correctness, statistical evaluation and manual risk testing."

# Phase 31 30 天学习与开发计划

## 每日安排

Day 1-3（每天 2-3h）：Learning Python environment、Tensor、NER/BIO；创建 pyproject/constants/preprocessing；验收能分词和校验 BIO。Day 4-6：Coding generator/vocabulary/tensor；验收三个 split 无完整句泄漏。Day 7-9：Learning Embedding/RNN/LSTM/BiLSTM；逐层创建 model；验收 shape 与 gradient。Day 10-12：Coding Dataset/DataLoader/training step；验收 loss 可下降。Day 13-15：Training/validation/checkpoint；验收可重载最佳 epoch。Day 16-18：Prediction/entity spans/redaction；验收字符 slice 与原文一致。Day 19-20：Evaluation；验收 per-class F1 和 Person recall。

Day 21：Learning Malaysian data ethics，生成并抽查本地标注。Day 22：Training 合入本地 train/validation。Day 23：Testing 独立 Malaysian test。Day 24：Coding FastAPI text endpoint。Day 25：Coding Web UI。Day 26：Coding TXT/PDF 与大小限制。Day 27：Testing 22 项并 Debugging。Day 28：Performance challenge 与失败分析。Day 29：GitHub/README/acceptance。Day 30（3-4h）：Presentation rehearsal、live demo fallback、最终 PDF 逐页检查。

每一天必须记录：学习内容、修改文件、实际命令、耗时、输出、PASS/FAIL；FAIL 未修复前不要进入依赖它的下一天。

# Phase 32 英文演示与面试准备

## A-M 教学卡

A 目标：5-10 分钟内解释问题、数据、模型、训练、评估、Demo、限制。B 前置：能读所有报告。C 概念：展示工程判断而非背术语。D 文件：`PRESENTATION_MATERIALS.md`。E 工具：浏览器、PowerShell、备用截图。F 增量：写逐分钟 script 与 15 个 Q&A。G 解释：先说 outcome，再用 shape/metric 支撑。H 关系：演示引用 README、acceptance、Web。I Run：计时彩排两次。J Expected：7-8 分钟，留问答时间。K Errors：现场训练风险高，准备已有 checkpoint；但要能展示训练命令和真实日志。L Checkpoint：能解释一次手测失败为何重要。M Interview："This is a reproducible educational prototype, not a production PII system."

# 最终 Code Evolution 总表

`model.py` V1 class -> V2 Embedding -> V3 BiLSTM -> V4 Linear -> V5 forward；`train.py` V1 Batch -> V2 Loss -> V3 Backprop -> V4 Epoch -> V5 Validation -> V6 Checkpoint；`app/main.py` V1 app -> V2 text API -> V3 UI -> V4 upload。最终 Appendix 的每个文件必须与当前验收仓库一致；阶段片段用于理解修改顺序，不能代替最终核对。

# 最终学习自检

你应能从空环境生成数据、解释每个 Tensor Shape、训练至少一轮、说明三行 Gradient 代码的顺序、从 checkpoint 新进程加载、解释 entity-level F1、启动网页、测试 TXT/PDF，并诚实陈述合成数据限制。做到这些，才能说：I understand it. I built it. I trained it. I tested it. I can explain it.

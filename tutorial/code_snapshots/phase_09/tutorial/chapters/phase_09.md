# Phase 09：Neural Network、Embedding、LSTM 与完整 BiLSTM

## 1. 本阶段学习目标

这一阶段从一个没有层、甚至不能 forward 的 Python class 开始，逐步完成六个可运行版本。结束时你要能独立创建模型、解释每一层、追踪每个 Tensor shape、执行 forward、计算参数数量，并说明为什么 `model(input)` 会调用 `forward()`。

我们不会直接展示最终 `src/model.py`。可运行中间文件位于 `tutorial/model_versions/model_v1.py` 到 `model_v6.py`；对应测试在 `tests/test_model_versions.py`。每次只增加一个概念，前一版本通过后才能继续。

## 2. 本阶段需要掌握的知识

Python：class、object、inheritance、`self`、constructor、`super()`、method。数学：输入、weight、bias、矩阵映射。PyTorch：Tensor、dtype、shape、`nn.Module`、parameter、Embedding、LSTM、bidirectional、Linear、Dropout、ReLU、concatenate、forward、train/eval、gradient。

具体 shape 统一用示例：batch=2、sequence=5、embedding=64、feature projection=8、hidden=96、num_labels=8。最终变化为 `(2,5)` -> `(2,5,64)`；features `(2,5,4)` -> `(2,5,8)`；拼接 `(2,5,72)`；BiLSTM `(2,5,192)`；Linear `(2,5,8)`。

## 3. 从零解释知识点

Neural Network 是带可训练数字的函数组合。输入经过计算得到输出；Loss 衡量输出与答案差距；backpropagation 计算每个 parameter 对 loss 的影响；optimizer 后续才更新 parameter。本阶段只搭建 forward，不训练，避免一次引入过多概念。

Layer 是一类可复用变换。Linear 做 `y=xW+b`；Embedding 按整数 ID 查一行向量；LSTM 逐时间步处理序列并维护状态。Parameter 是训练会改变的 Tensor，普通局部变量不是 parameter。PyTorch Module 会自动收集子 Module 的 parameter，支持 `.to(device)`、`.train()`、`.eval()`、保存与加载。

## 4. 本阶段开始前的项目状态

```text
tutorial/model_versions/
  model_v1.py  [本阶段创建]
  model_v2.py  [本阶段创建]
  model_v3.py  [本阶段创建]
  model_v4.py  [本阶段创建]
  model_v5.py  [本阶段创建]
  model_v6.py  [本阶段创建，等价于最终架构]
tests/test_model_versions.py [本阶段创建]
src/model.py                  [最终正式文件，阶段结束后同步]
```

Phase 08 已提供 `input_ids` shape `(batch,length)`、features `(batch,length,4)`、mask `(batch,length)`。本阶段只消费 input_ids/features；mask 在 loss/metrics 阶段使用。

## 5. 本阶段需要使用的工具

VS Code 同时打开版本文件与测试。PowerShell 位于项目根目录，激活 `.venv`。每个版本可单独执行 pytest，例如：

```powershell
python -m pytest tests\test_model_versions.py::test_version_2_embedding_shape -q
```

失败时在 VS Code 测试函数左侧设置 breakpoint，查看 tensor 的 `.shape` 和 `.dtype`。

### 6. Lesson 1：什么是 Neural Network？

先不用 PyTorch。设输入 x=3，weight=2，bias=1，则输出 `3*2+1=7`。如果正确答案是 10，模型需要调整 weight/bias。神经网络不是“会思考的黑盒”，而是许多可微计算和 parameter 的组合。

操作练习：在 Python terminal 输入 `x=3; weight=2; bias=1; print(x*weight+bias)`，应输出 7。这段代码不是训练，只帮助区分 input 与 parameter。NER 的 input 是 token IDs；parameter 包括 embedding 表、LSTM weights 与 classifier weights；output 是每 token 的 label logits。

### 7. Lesson 2：什么是 Layer？

Layer 接收 Tensor 并返回 Tensor。多个 layer 像流水线，但每步 shape 可能变化。Linear layer 对最后一维做矩阵映射。例如输入最后一维 192，输出类别 8，则 `nn.Linear(192,8)` 的 weight shape 是 `(8,192)`、bias shape `(8,)`。

执行：

```powershell
python -c "import torch; from torch import nn; layer=nn.Linear(3,2); x=torch.ones(4,3); print(layer(x).shape)"
```

实际预期 `torch.Size([4, 2])`。第一维 4 保留，最后维 3 变 2。

### 8. Lesson 3：什么是 Parameter？

Parameter 是 `requires_grad=True` 且被 Module 注册的 Tensor。执行：

```powershell
python -c "from torch import nn; m=nn.Linear(3,2); [(print(n,p.shape,p.requires_grad)) for n,p in m.named_parameters()]"
```

会看到 weight/bias。普通 `self.number=3` 不会出现在 named_parameters。未来 optimizer 只更新注册 parameter。参数量计算是每个 shape 维度相乘后求和；不是源代码行数。

### 9. Lesson 4：什么是 PyTorch Module？

`nn.Module` 是所有 PyTorch layer/model 的基类。它实现参数登记、子模块树、设备移动、train/eval mode、state_dict、hook 与 `__call__`。我们组合已有 layer 时，自己的模型也应继承 Module。

不要直接写一个普通函数持有全局 weights；那会让保存、加载、optimizer 和 device 管理困难。Module 不会自动决定网络结构，结构仍由你在 constructor 和 forward 中明确编写。

### 10. Lesson 5：Python Class、Inheritance、self 与 super

语法 `class BiLSTMNER(nn.Module):` 定义子类。`BiLSTMNER` 是我们命名的模型蓝图；括号里的 `nn.Module` 是父类。创建 `model=BiLSTMNER()` 得到 object。`self` 指这个 object。

`__init__` 是 constructor。第一行必须 `super().__init__()`，让父类建立 `_parameters`、`_modules` 等内部容器。若先赋 `self.embedding=nn.Embedding(...)` 而不初始化父类，PyTorch 会报错或无法登记层。`super()` 不是创建第二个模型，而是从当前继承链访问父类实现。

### 11. Lesson 6：Version 1 - 创建第一个模型类

打开 `tutorial/model_versions/model_v1.py`，逐行输入：

```python
from torch import nn

class BiLSTMNER(nn.Module):
    def __init__(self) -> None:
        super().__init__()
```

此版本能实例化，但没有 forward。运行：

```powershell
python -m pytest tests\test_model_versions.py::test_version_1_instantiates_module -q
```

真实结果 `1 passed`。局部测试只验证 inheritance/constructor。若调用 `model(torch.tensor(...))`，应得到缺少 forward 的 NotImplementedError；这不是 bug，而是 Version 1 的已知边界。

### 12. Lesson 7：理解 Embedding

Vocabulary 把词映射整数，例如 `<PAD>=0, <UNK>=1, sarah=2`。整数大小没有语义；ID 2 不代表比 ID 1 更大。Embedding 是 shape `(vocab_size,embedding_dim)` 的可训练查找表。

输入 IDs `(2,5)` 表示两句、每句五个位置。查表后 `(2,5,64)`：每个整数变成 64 个浮点数。`padding_idx=0` 让 padding row 在训练中不更新。Embedding 随机初始化，训练才让向量适合 NER；本项目没有加载预训练词向量。

### 13. Lesson 8：Version 2 - 添加 Embedding

复制 V1 为 `model_v2.py`，修改 constructor 接收 `vocab_size` 和 `embedding_dim`，加入：

```python
self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
```

为局部测试暂时加入 `embed()`：

```python
def embed(self, input_ids: torch.Tensor) -> torch.Tensor:
    return self.embedding(input_ids)
```

执行 Version 2 测试，真实结果通过：输入 `[[2,3,0]]` shape `(1,3)`，输出 `(1,3,16)`。若 dtype 是 float，Embedding 报 Expected Long；ID 必须 `torch.long`。若 ID>=vocab_size，会 IndexError。

### 14. Lesson 9：理解 RNN 与 LSTM

普通 feed-forward layer 独立处理 token，无法知道左侧词。RNN 逐位置更新 hidden state：当前位置结合当前输入和上一状态。长序列中梯度可能消失/爆炸。

LSTM 用 input/forget/output gates 控制 cell state。门是 0 到 1 的可学习比例。无需手算所有公式，但必须知道输入 shape `(batch,length,input_size)`；输出 `encoded` 保存每个位置 hidden representation；另有最后 hidden/cell state。本项目需要每 token 预测，所以用完整 encoded，不只最后状态。

### 15. Lesson 10：理解 Bidirectional LSTM

单向 LSTM 只看左侧。NER 中 `Bank` 后面的词可能决定它是机构名称。Bidirectional 运行一条左到右 LSTM 和一条右到左 LSTM，再拼接同一位置结果。

若 `hidden_dim=96` 表示每个方向 96，则输出最后维是 192，不是 96。这个乘 2 是常见 classifier shape mismatch 根源。它不是把句长乘 2；batch 和 length 不变。

### 16. Lesson 11：Version 3 - 添加 BiLSTM

V3 constructor 在 Embedding 后加入：

```python
self.lstm = nn.LSTM(
    embedding_dim,
    hidden_dim,
    batch_first=True,
    bidirectional=True,
)
```

`batch_first=True` 让 shape 是 `(batch,length,features)`，与 Dataset 一致。局部 `encode` 先 embedding，再 `encoded,_=self.lstm(embedded)`。下划线表示我们暂不使用最终 states。

测试用 embedding=16、hidden=12，输入 `(1,3)`，输出应 `(1,3,24)`。实际 Version 3 测试通过。若忘记 bidirectional，最后维是 12，测试会立即失败。

### 17. Lesson 12：理解 Linear Layer

LSTM 输出每 token 192 个上下文特征，但标签空间只有 8：PAD、O、B/I-PER、B/I-LOC、B/I-ORG。`nn.Linear(192,8)` 对每个 token 独立做相同映射，输出 logits。

Logit 是未归一化分数，可以负数且和不为 1。训练 CrossEntropyLoss 内部做 log-softmax，因此 forward 不应先 softmax。推理 argmax 选择最大 logit 的 label ID。

### 18. Lesson 13：Version 4 - 添加 Linear

由于双向输出是 `hidden_dim*2`，加入：

```python
self.classifier = nn.Linear(hidden_dim * 2, num_labels)
```

暂时用 `classify()` 串起 embedding -> LSTM -> classifier。num_labels 来自实际 label list 长度，不能硬编码 7；本项目 checkpoint 包含 PAD 共 8。

Version 4 测试输入 `(1,3)`，输出 `(1,3,8)`。若 Linear 写 hidden_dim 而非乘 2，会报 mat1/mat2 shapes cannot be multiplied；打印 encoded.shape 即可定位。

### 19. Lesson 14：理解 Dropout

Dropout 在训练时随机把部分特征设 0，减少模型依赖单一神经元；推理时必须关闭随机屏蔽。`model.train()` 开启，`model.eval()` 关闭。eval 不等于 no_grad：eval 控制层行为，no_grad 控制是否记录梯度，两者职责不同。

V4 在 classifier 前加入 `self.dropout=nn.Dropout(0.25)`。测试调用 `model.eval()` 后 `model.dropout.training` 为 False。不要在 validation 忘记 eval，否则指标会随机波动。

### 20. Lesson 15：Version 5 - 实现 forward()

把临时 `classify` 改成标准：

```python
def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
    embedded = self.embedding(input_ids)
    encoded, _ = self.lstm(embedded)
    return self.classifier(self.dropout(encoded))
```

通常调用 `model(input_ids)`，而不是 `model.forward(input_ids)`。Module 的 `__call__` 会执行 hooks、autocast 等机制后调用 forward。参数 input_ids 来自 DataLoader，dtype long，shape `(batch,length)`；返回 float logits `(batch,length,num_labels)`。

Version 5 测试还执行 `logits.sum().backward()`，确认 classifier weight 得到 gradient。真实结果通过。Backward 只计算 gradient，本阶段没有 optimizer 更新。

### 21. Lesson 16：完整 Tensor Shape Tracking

使用实际配置：IDs `(2,5)` long。Embedding `(2,5,64)` float。额外 casing features 原始 `(2,5,4)` float，projection 后 `(2,5,8)`。`torch.cat(...,dim=-1)` 后 `(2,5,72)`。

LSTM input_size 必须 72，输出 `(2,5,192)`。Dropout shape 不变。Linear 只改最后维，logits `(2,5,8)`。Argmax(dim=-1) 后 `(2,5)` long。Gold labels 同为 `(2,5)`，mask 也是 `(2,5)` bool。

具体元素数：input IDs 10 个整数；embedding 输出 640 个 float；combined 720；encoded 1920；logits 80。Shape 不是任意格式，每一层 constructor 必须与上一层最后维匹配。

### 22. Lesson 17：Version 6 - 连接真实 casing features

最终模型利用 `[is_title,is_upper,is_lower,has_digit]` 四特征，帮助未见词。加入：

```python
self.feature_projection = nn.Linear(4, 8)
```

LSTM input_size 改 `embedding_dim+8`。forward 新参数 features；先 ReLU projection，再 cat。`dim=-1` 表示最后维，不应沿 batch 或 sequence 拼接。

Version 6 测试传 IDs `(1,3)`、features `(1,3,4)`，得到 logits `(1,3,8)`。这与正式 `src/model.py` 架构一致。若 features length 与 IDs 不同，cat 报 size mismatch，应回到 collate 检查。

### 23. Lesson 18：连接真实 Dataset 并完整 Forward

真实 batch 是 dict：`batch['input_ids']`、`batch['features']`、`batch['labels']`、`batch['mask']`。调用：

```python
logits = model(batch["input_ids"], batch["features"])
assert logits.shape[:2] == batch["input_ids"].shape
assert logits.shape[-1] == len(LABELS)
```

labels 不传给 model；它们给 loss。mask 也不改变 forward，本项目用它排除 padding metrics。完整 forward 测试不需要训练整个 epoch，因此几秒即可定位接口错误。

### 24. Lesson 19：常见错误与 Debugging

Shape mismatch：逐层 print shape，检查 LSTM input_size 与 bidirectional*2。Wrong dtype：Embedding IDs 必须 long，features float。Invalid vocabulary index：确保所有 ID 小于 vocab_size，UNK 处理未知词。Device mismatch：model 与所有 tensors 都 `.to(device)`。

Missing forward：V1 故意会发生，V5 后必须解决。Incorrect num_labels：用 checkpoint labels 长度。Features shape 错：最后维必须 4。忘记 `super()`：层登记失败。训练/推理 mode 错：validation 调 eval。不要用 try/except 隐藏 shape 错误；让测试失败并读取 traceback 最后一行。

### 25. Lesson 20：阶段验收与参数数量

运行：

```powershell
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
python -m pytest tests\test_model_versions.py -q
python -m pytest tests\test_model.py -q
python -c "from src.model import BiLSTMNER; m=BiLSTMNER(100,8); print(sum(p.numel() for p in m.parameters()))"
```

本轮 Version 测试真实结果 `6 passed in 1.67s`。参数数随 vocab_size 变化；最终 checkpoint 使用实际 vocabulary，总计 143,536。学生必须能解释为什么 embedding 参数与 vocab_size 成正比、BiLSTM 输出为何乘 2、Linear 输出为何等于标签数。

## 10. 完整代码回顾

不要把六版混成一个文件。依次打开 `tutorial/model_versions/model_v1.py` 到 `model_v6.py`，使用 VS Code Compare Selected 对比。V1 只有 Module；V2 embedding；V3 LSTM；V4 dropout/classifier；V5 standard forward；V6 features。

阶段最终正式文件是 `src/model.py`。它与 V6 层结构一致，但包含更完整中文 docstring/shape 注释。任何正式代码修改都必须同步 V6、测试、Phase 09 与快照 hash。

## 11. 跨文件调用关系

`src/dataset.py` 产生 batch -> `src/train.py` 调 `model(input_ids,features)` -> Module `__call__` 调 `forward` -> logits 传 CrossEntropyLoss。`src/predict.py` 重建同一 model、load_state_dict、eval/no_grad、argmax。配置来自 checkpoint，标签来自 `src/constants.py`。

## 12. 数据流解释

tokens list -> vocabulary integer IDs -> Dataset long Tensor `(sentence_length,)` -> collate padded `(batch,max_length)` -> Embedding/context/features -> logits `(batch,max_length,8)`。模型不会返回实体文字；BIO decoding 在 prediction 层完成。分层职责让训练与 API 共用同一个 model。

## 13. 常见错误

除 Lesson 19 外，常见教学错误是一次复制 V6 后无法解释每行。解决方法是删除自己的练习副本，从 V1 重建，每版只看一个测试。另一个错误是把 hidden_dim=96 理解为双向总维；本项目定义为每方向，因此总输出 192。

## 14. Checkpoint

必须满足：六个版本测试全部通过；能画出具体 shapes；能解释 class/object/inheritance/self/super；能说明 parameter 与普通 variable 差异；能运行真实 batch forward；能计算并解释参数量。任何一项不能解释都回到对应 Lesson。

## 15. 学生练习

1. 将 V2 embedding_dim 改 32，预测输出 shape 后运行验证。
2. 将 V3 bidirectional=False，记录 shape 变化，再恢复。
3. 故意把 V4 classifier 输入写 hidden_dim，阅读错误。
4. 比较 train/eval 下 dropout 两次输出。
5. 用 `named_parameters()` 列出层名和 shape。

## 16. 面试准备

"My model maps token IDs to trainable embeddings and concatenates four casing features. A bidirectional LSTM encodes left and right context. Its output has twice the per-direction hidden size. Dropout regularizes training, and a linear layer produces one logit for each BIO label at every token. I built and tested the architecture in six incremental versions."

## 17. 下一阶段预告

Phase 10 使用 V6/正式 model 的 logits 学习 CrossEntropyLoss、gradient、backpropagation、zero_grad 与 optimizer.step。模型结构不再改变；重点从“如何计算输出”转到“参数如何从标注数据学习”。

## 补充 A：`BiLSTMNER.__init__` 完整函数教学卡

Function name 严格说是特殊方法 `__init__`。Purpose 是接收超参数并创建需要长期保存在 object 中的 layer。Parameters：`self` 是当前 model；`vocab_size:int` 是训练 vocabulary 项目数；`num_labels:int` 是标签数；embedding/hidden 是维度；dropout 是 0 到 1 的比例。Return type 标注 None，因为 constructor 初始化 object，不把新值 return 给调用者。

Calling code 在 `src/train.py` 与 `src/predict.py`。它内部调用父类 Module constructor，再调用 `nn.Embedding`、`nn.Linear`、`nn.LSTM`、`nn.Dropout` constructors。Example input 是 `BiLSTMNER(vocab_size=100,num_labels=8,embedding_dim=64,hidden_dim=96)`；example output 是可调用 Module object，不是 logits。

为什么 layers 放 `__init__` 而不是 forward 内？如果每次 forward 新建 layer，每次都会随机生成新 parameter，optimizer 与 checkpoint 无法追踪。把 layer 赋给 `self` 后，Module 的 `__setattr__` 会登记它。检查：

```powershell
python -c "from src.model import BiLSTMNER; m=BiLSTMNER(100,8); print(dict(m.named_children()).keys())"
```

预期包含 embedding、feature_projection、lstm、dropout、classifier。Common errors：vocab_size=0；dropout 超范围；hidden_dim 与 checkpoint 不一致；先创建 layer 后调用 super。

## 补充 B：`forward` 完整函数教学卡

Function name `forward`。Purpose 是描述一个 batch 从输入到 logits 的确定性计算图。Parameters：`self`；`input_ids:torch.Tensor`，long，shape `(B,L)`；`features:torch.Tensor`，float32，shape `(B,L,4)`。Return value 是 float logits；return type Tensor；shape `(B,L,C)`。

Calling function 通常不是手写 `forward`，而是 Module 的 `__call__`，由 `model(input_ids,features)` 触发。Forward 内调用 embedding、feature projection、ReLU、cat、LSTM、dropout、classifier。它不调用 loss、不执行 backward、不更新 parameter。这种职责分离允许同一 forward 在 training、validation、prediction 中复用。

Example input：

```python
input_ids = torch.tensor([[2, 3, 0], [4, 5, 6]], dtype=torch.long)
features = torch.zeros((2, 3, 4), dtype=torch.float32)
logits = model(input_ids, features)
```

B=2、L=3、C=8，output shape `(2,3,8)`。Logits 的 48 个 float 还不是 BIO string；后续 argmax -> label IDs -> label mapping。Common errors：把 labels 当 features；features 缺最后维；IDs 用 float；batch/length 不同；model 在 GPU 但 tensors 在 CPU。

## 补充 C：一次完整数值 Shape 演算

假设两个句子 padding 后长度 5：

```text
input_ids = [[2,3,4,5,0], [6,7,8,9,10]]
shape=(2,5), dtype=int64
```

Embedding table 假设 vocab=100、dim=64，参数 shape `(100,64)`，共 6,400 parameter。查表不改变前两维，输出 `(2,5,64)`，共 640 float。注意 padding 位置仍有向量，只是 padding row 固定/不更新；loss 还需 ignore padding。

四特征 `(2,5,4)` 共 40 float。Linear(4,8) 对十个 token 分别映射，输出 `(2,5,8)`。Weight `(8,4)=32`，bias 8，共 40 parameter。ReLU 将负数置 0，shape 不变。

Cat 沿最后维连接 64+8=72，输出 `(2,5,72)`。若 `dim=1` 会试图拼 sequence，得到错误语义 `(2,10,64/8)` 且最后维不等；正确是 `dim=-1`。

BiLSTM 输入 `(2,5,72)`。每方向 hidden=96；两个方向同位置拼接，输出 `(2,5,192)`。PyTorch LSTM 还返回 h_n/c_n，shape `(2,2,96)`：第一维 2 是方向数，第二维 2 是 batch，不要与 sequence length 混淆。本任务不使用最后 states。

Dropout `(2,5,192)` -> `(2,5,192)`。Linear(192,8) weight `(8,192)` 共 1,536，bias 8。输出 `(2,5,8)` 共 80 logits。argmax(-1) 变 `(2,5)`。每个位置得到一个 label ID；mask 决定哪些位置是真 token。

## 补充 D：LSTM 参数为什么比想象多

LSTM 不只有一个 weight。每方向有 input/forget/cell/output 四组门。粗略单层单方向参数包含 `4*hidden*input_size`、`4*hidden*hidden` 和 biases。双向再乘 2。可用 PyTorch 而非手抄公式核对：

```powershell
python -c "from src.model import BiLSTMNER; m=BiLSTMNER(100,8); [(print(n,tuple(p.shape),p.numel())) for n,p in m.named_parameters()]"
```

你会看到 `weight_ih_l0`、`weight_hh_l0`、bias，以及 `_reverse` 版本。`ih` 连接 input-to-hidden，`hh` 连接 hidden-to-hidden。总参数量依赖 vocab_size，因此教学小模型与最终 checkpoint 数量不同。最终 143,536 来自实际 vocabulary/config，不应硬编码在代码。

## 补充 E：Version 1 到 Version 6 的逐行变更清单

V1 新增 import nn、class header、constructor、super；可实例化。V2 新增 torch import、两个 constructor parameters、Embedding attribute、embed method；可验证查表。V3 新增 hidden_dim、LSTM attribute、encode method；可验证上下文 shape。V4 新增 num_labels/dropout、Dropout/Linear、classify method；可验证分类维度和 mode。V5 只将临时 classify 变标准 forward；让 Module 调用机制和 gradient 测试成立。V6 新增 feature projection、forward 第二参数、ReLU 与 cat，并修改 LSTM input_size。

为什么不在 V2 就写最终 forward？因为当时输出只是 embedding，不是模型最终语义；命名为 embed 能诚实表达局部功能。为什么 V3 用 encode？它输出 contextual representation。V4 classify 已能返回 logits，但 V5 才教授 PyTorch 标准接口。这种临时 method 在最终版本删除，是正常 incremental development，不是遗留 API。

对比命令：

```powershell
git diff --no-index tutorial\model_versions\model_v3.py tutorial\model_versions\model_v4.py
```

`--no-index` 比较任意两个文件，不要求 Git commit。退出码 1 表示有差异，不等于命令损坏。你应看到 Dropout、Linear 和 num_labels，而不是无关数据代码。

## 补充 F：五个可复现 Debug Lab

Lab 1 Shape mismatch：在自己的临时副本把 classifier 改 `nn.Linear(hidden_dim, num_labels)`，运行 V4 test，读取 `mat1 and mat2 shapes`。写下实际 encoded 最后维 24 与错误期望 12，再恢复。不要修改正式文件。

Lab 2 Wrong dtype：运行 `model.embed(torch.tensor([[2.0]]))`，观察 Embedding 对 float ID 的错误。修复是 dtype long，不是把 embedding weight 改整数。

Lab 3 Invalid index：vocab_size=20 时输入 ID 20（合法范围 0-19），观察 index out of range。正式修复是 unknown token 映射 `<UNK>=1`，不能扩大 vocab 掩盖预处理错误。

Lab 4 Device mismatch：有 GPU 才执行。把 model `.to('cuda')` 但 input 留 CPU，会报设备不一致。统一 device。CPU 学生只需解释，不伪造 GPU 输出。

Lab 5 Missing forward：实例化 V1 后调用 model，观察 NotImplementedError；对比 V5 成功。它证明 Module class 并不会自动猜测 layer 顺序。

每个 Lab 的目标是阅读 traceback、定位自己文件行号、打印 shape/dtype、修复根因。不得用宽泛 try/except 把错误吞掉，否则训练可能产生错误而不被发现。

## 补充 G：为什么当前选择 BiLSTM Token Classifier 而不是 CRF

理想架构可在 Linear 后加 CRF，让整个标签序列联合打分并学习转移，例如 I-PER 不应直接跟 B-LOC。当前比赛规范允许在完整 CRF 超出教学/时间范围时使用自行定义 BiLSTM token classifier。我们选择 fallback 的原因是 CPU 训练、零基础复现和调试更直接；核心 NER 仍是自己训练。

代价必须明确：每 token argmax 可能产生非法初始 I-tag；prediction 会把不合法 I 安全视为新实体开始，但这不是 CRF 联合解码。后续改进可以在完全理解当前 loss/mask 后实现 CRF，并增加转移约束测试。不能在没实现 CRF 时把标题写成 BiLSTM-CRF。

## 补充 H：本阶段掌握证明

学生不看代码，画出五个 box：IDs、Embedding+features、BiLSTM、Dropout、Linear；在每条箭头写 shape。然后打开空文件，在 20 分钟内写 V1/V2，并让两项测试通过。再口头解释 super、parameter、bidirectional*2、logit、train/eval。

最后提交一份错误日志：选择一个 Debug Lab，保留错误信息、原因、修复 diff 和修复后 PASS。只有“能从失败恢复”才能证明不是机械复制。教师检查六项测试和学生解释，而不是只看最终文件存在。

## 补充 I：逐行阅读最终 forward 的口述练习

第一行 `embedded = self.embedding(input_ids)`：调用已经登记的 Embedding object，输入 long IDs，返回 float vectors。第二行 feature projection：四个手工特征通过可训练 Linear，再用 ReLU 引入非线性。第三行 cat：不改变 batch/sequence，只扩展每个 token 的描述。

第四行 `encoded, _ = self.lstm(combined)`：LSTM 返回两个对象，我们保留所有位置的 contextual states，暂时丢弃最终 hidden/cell。第五行先 dropout 再 classifier：训练时随机正则化，最后为每个 token 产生八个 logit。Return 把 Tensor 交给调用者，不在函数内 print，也不把 argmax 固定进模型，以便 CrossEntropyLoss 使用完整 logits。

学生应分别回答：如果删除 ReLU，shape 是否改变？不会，但数值变换能力不同。如果 cat 改成相加，为什么失败？64 与 8 维无法直接相加，而且会丢失独立特征。如果 forward 返回 argmax，为什么不能训练？离散 argmax 不适合 CrossEntropyLoss 的 logits 输入，也切断有用梯度信息。

## 补充 J：代码审查清单

检查所有 layer 只在 constructor 创建；super 位于 layer 前；padding_idx 等于 vocabulary PAD；LSTM input_size=embedding_dim+8；bidirectional=True；classifier 输入 hidden_dim*2；forward 参数和 DataLoader keys 一致；没有 softmax；没有外部 NER pipeline；docstring 与实际 shape 一致。

运行 `python -m pytest tests\test_model_versions.py tests\test_model.py -q` 后再进入训练。若只通过 V6 而早期版本失败，教学演化仍不完整；六个版本都是交付的一部分。

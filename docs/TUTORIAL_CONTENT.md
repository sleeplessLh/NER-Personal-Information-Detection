# Personal Information Detection in Text Using NER

## 经过真实训练、测试与验收的零基础中文教程

版本：1.0

验证日期：2026-10-28（Asia/Singapore）

适用读者：会基础 Python、尚未系统学习 Machine Learning 的大学一年级学生。

重要声明：本教程中的命令、checkpoint、日志、指标和 API 测试均来自本项目的真实 Windows 11 执行。当前数据是透明生成的合成语料；测试集实体与完整句子不泄漏，但句法模板相似，所以 1.0000 F1 不能代表真实生产性能。没有真实初学者参与试读，因此不声称已通过真实用户可理解性测试。

# Chapter 1 项目介绍

本项目解决文本中的 Personal Information Detection：输入一段原始英文，系统找出 PERSON（人名）、LOCATION（地点）和 ORGANISATION（机构），再生成脱敏文本。核心预测由我们自己训练的 PyTorch BiLSTM 完成，不使用 OpenAI、Gemini、Cloud NER 或现成 NER pipeline。

完整链路是：Raw Text -> Tokenization -> Token IDs + casing features -> Embedding -> Bidirectional LSTM -> Linear Layer -> BIO Tags -> Entity Spans -> JSON -> Redaction/Web UI。

最终交付包括训练代码、checkpoint、独立评估、FastAPI、TXT/PDF 上传、15 个自动化测试、真实实验日志与本 PDF。

Checkpoint Questions：为什么正则表达式不能成为本项目的核心 NER？参考答案：规则只能匹配预先写下的模式，不能通过 loss 与 gradient 从标注数据学习；比赛明确要求自己训练的模型。正则只用于支持性的 Tokenization，不决定实体类别。

# Chapter 2 Machine Learning 基础

Machine Learning（机器学习）让程序从数据中调整参数，而不是由开发者写出所有判断规则。Supervised Learning（监督学习）使用“输入 + 正确答案”训练。本项目输入是 token 序列，答案是每个 token 的 BIO label。

Deep Learning（深度学习）使用多层 Neural Network。参数是模型内部可学习的数字。训练一次 batch 时，模型先做 forward pass 得到 logits，再由 Cross Entropy Loss 衡量错误，Backpropagation 计算每个参数应如何变化，Optimizer 执行更新。

Gradient（梯度）可以理解为 loss 对参数的局部斜率。Learning Rate（学习率）控制每次沿下降方向迈多大一步。Epoch 表示完整看完一次 training set；Batch 是一次并行处理的样本小组。本项目 batch size=64，learning rate=0.003。

Overfitting（过拟合）是训练集非常好、未见数据很差。首轮实验 train loss 很快接近 0，但 validation F1 只有 0.1976，就是模型背记实体词。Underfitting（欠拟合）是连训练规律都学不好。最终通过 word dropout 迫使模型学习上下文。

Checkpoint Questions：如果删除 optimizer.step() 会怎样？参考答案：backward 仍会计算 gradient，但参数永远不更新，模型不能学习。

# Chapter 3 NLP、NER 与 BIO

Natural Language Processing（自然语言处理）研究如何让计算机处理人类语言。Named Entity Recognition（命名实体识别）是 sequence labeling：每个 token 都获得一个标签。

BIO Tagging 使用 B 表示实体开始、I 表示实体内部、O 表示不属于实体。例如 `Ali/B-PER studies/O at/O Universiti/B-ORG Teknologi/I-ORG Malaysia/I-ORG`。没有 BIO 时，三个连续机构词无法明确是一个三词实体还是三个实体。

Token-level accuracy 逐 token 计分，容易被大量 O 标签抬高。Entity-level F1 要求 span 起止位置和类型都完全正确，更符合脱敏风险。本项目报告后者。

Checkpoint Questions：`I-LOC` 能否直接出现在句首？参考答案：规范 BIO 中不能；预处理校验会拒绝这种 gold label。模型偶尔可能输出非法 I，推理抽取器会把它安全地视为新实体开始。

# Chapter 4 Windows 11、VS Code 与环境

使用工具：Windows 11、VS Code、PowerShell、uv。操作位置：VS Code Integrated Terminal。先安装 VS Code，再从 Extensions 安装 Microsoft Python 扩展。用 File -> Open Folder 打开项目，然后 Ctrl+Shift+P 选择 Python: Select Interpreter，选择 `.venv\Scripts\python.exe`。

执行命令：`uv sync --all-groups`。预期结果：创建 `.venv` 并按 `uv.lock` 安装依赖。运行 `uv run python -c "import torch; print(torch.__version__)"`，本机实际输出 `2.9.0+cpu`。

Debugger：在行号左侧点击设置 breakpoint，按 F5，选择 Python Debugger。Variables 面板查看 tensor；Debug Console 可输入 `tensor.shape`。错误应从 traceback 最后一行开始读，再向上找自己的文件与行号。

常见错误：PowerShell 找不到 uv 时，重开终端并确认安装目录在 PATH；interpreter 错误时重新选择 `.venv`；不要把系统 Python 与项目环境混用。

# Chapter 5 项目架构

`generate_data.py` 产生数据；`preprocessing.py` 负责 Tokenization、Vocabulary 与 BIO 校验；`dataset.py` 把样本转成 tensor 并 padding；`model.py` 定义网络；`train.py` 调用前述模块并保存 checkpoint；`evaluate.py` 只读冻结模型与 test set；`predict.py` 加载模型并抽取 span；`redact.py` 替换实体；`app/main.py` 暴露网页和 API。

File Dependency Diagram：generate_data -> processed JSONL；preprocessing + dataset + model -> train -> best_model.pt；best_model.pt + predict + redact -> FastAPI -> Browser。

数据流：浏览器 JSON -> Pydantic 校验 -> tokenize -> input IDs/features -> logits -> argmax BIO -> entity list -> redaction -> JSON response -> JavaScript 显示。

# Chapter 6 Dataset

本项目没有假装下载成功任何公开数据集。首版使用可完全复现的合成数据：人名是合成示例，地点和机构是公开名称。train/validation/test 分别为 2400/300/300 行。生成器对规范化完整句子执行跨 split 交集检查，发现泄漏就抛错；实体词表也分离。

Training Set 用来更新参数；Validation Set 用来选择 epoch 和改进方案；Test Set 只在模型冻结后评估。不能根据 test label 反复调整模型。本项目保留了每轮真实结果，但教学实验仍共享模板分布，属于重要限制。

Malaysian challenge 使用公开地点/机构和合成人名，不包含真实私人资料。真实比赛前，应由两名标注者依书面 guideline 独立标注，计算一致率，解决分歧，并将文档级来源隔离后再切分。

运行验证：`uv run python -m src.generate_data`。预期打印三组 rows/unique_sentences；若有 leakage，命令失败而不是静默继续。

# Chapter 7 Preprocessing

Tokenization（分词）把原始字符串拆成 token。本项目的正则保留英文单词、连字符/撇号名字、数字和标点。`normalize_token` 仅为词表转小写；原 token 保留大小写用于显示和 features。

Vocabulary（词表）把 token 映射为整数。`<PAD>=0` 补齐 batch；`<UNK>=1` 代表训练词表未见词。例：`[Ali, works, .] -> [23, 87, 4]`；未知 `John` 可能变成 1。ID 不是语义大小，只是索引。

大小写特征是 `[is_title,is_upper,is_lower,has_digit]`。`Ali -> [1,0,0,0]`，`UTM -> [0,1,0,0]`。它帮助 OOV 词仍保留形式信息。

如果删除 BIO 校验，错误标注可能进入训练，模型会被迫学习矛盾目标。验证命令：`uv run pytest tests/test_preprocessing.py -q`。

# Chapter 8 Model Architecture

`nn.Module` 是 PyTorch 模型基类。`__init__` 创建需要保存参数的层；`super().__init__()` 注册 PyTorch 内部机制。不要直接调用 `forward`；执行 `model(input_ids, features)` 时 `nn.Module.__call__` 会处理 hooks 后调用 forward。

Tensor shape 示例：batch=2、sequence length=5。input IDs 为 `(2,5)`；Embedding 64 维后为 `(2,5,64)`；features `(2,5,4)` 经 Linear 为 `(2,5,8)`；concatenate 为 `(2,5,72)`；双向 LSTM 每方向 96，输出 `(2,5,192)`；classifier 输出 8 个标签 logits，shape `(2,5,8)`。

Embedding 是可学习查找表，不是 one-hot。BiLSTM 同时从左到右与右到左读取，使 `Malaysia` 的表示使用前后文。Hidden State 是 LSTM 对上下文的压缩表示。Linear Layer 将 192 维上下文映射为 8 个未归一化 logits。

Softmax 把 logits 转概率，但 `CrossEntropyLoss` 内部已结合 log-softmax，所以训练代码不要先 softmax。argmax 只用于推理标签，不可微，不能用于 loss。

# Chapter 9 Training

训练循环顺序不能随意换：`optimizer.zero_grad()` 清空上个 batch 累积的 gradient；forward 产生 logits；loss 比较 logits 与 gold labels；`loss.backward()` 用链式法则计算梯度；gradient clipping 限制爆炸；`optimizer.step()` 更新参数。

Padding label ID=0，loss 的 `ignore_index=0`，否则模型会大量学习预测 padding。mask 则用于从指标中排除 padding。

本项目用 entity word dropout=0.8 和 ordinary word dropout=0.15。它只在训练 Dataset 中把部分 token ID 替换为 `<UNK>`，大小写和 gold label 不变；validation/test 不做 dropout。这个决策来自真实失败实验，而不是装饰性复杂度。

执行：`uv run python -m src.train --epochs 10 --batch-size 64`。最终最佳 epoch=3，validation F1=0.9685。重复训练即使 seed 固定，也可能因硬件并行与库实现产生轻微差异。

# Chapter 10 Evaluation

Precision=TP/(TP+FP)，回答“模型报出的实体中多少正确”；Recall=TP/(TP+FN)，回答“真实实体中多少被找到”；F1 是二者调和平均。脱敏中特别重视 recall，因为漏掉姓名可能造成隐私泄露，但 precision 太低会毁坏可用文本。

本项目采用 exact entity span：类型与边界必须都一致才算 TP。最终合成 test 的 PER/LOC/ORG 与 overall 均为 1.0000；这反映模型掌握当前模板，不证明真实域完美。

执行：`uv run python -m src.evaluate`。输出同时保存到 `reports/test_metrics.json`。

# Chapter 11 Inference

`Predictor.__post_init__` 用 `torch.load(..., map_location='cpu')` 读取 checkpoint，按保存的 config 重建同一架构，再 `load_state_dict`。`model.eval()` 关闭 dropout；`torch.no_grad()` 避免构建训练计算图，节省内存。

完整追踪 `Ali studies at Universiti Teknologi Malaysia.`：tokens 是 7 项 list；IDs shape `(1,7)`；padding 在单句时无需增加；embedding `(1,7,64)`；BiLSTM `(1,7,192)`；logits `(1,7,8)`；argmax 得到 PERSON/O/ORG BIO；extract_entities 合并三个 ORG token；最终 JSON 返回两个实体。

# Chapter 12 Redaction

脱敏函数按 token index 扫描。遇到实体 start 时只输出一次 `[TYPE]`，然后跳到 end token；普通 token 原样保留。最后修复标点前空格。实体位置完全来自模型，不使用关键词表决定类别。

删除 `index = entity['end_token']` 会导致多词实体内部 token 再次输出，产生隐私泄漏。验证：`uv run pytest tests/test_redaction.py -q`。

# Chapter 13 FastAPI Backend

GET `/` 返回简单 HTML，状态 200。POST `/api/predict` 接收 JSON `{"text": string}`；Pydantic 要求长度 1 到 100000，成功 200，空文本 422。POST `/api/upload` 接收 multipart `file`；TXT 要 UTF-8，PDF 用 pypdf 提取文字；不支持扩展名返回 415，无可提取文本返回 400。

`get_predictor` 实现进程内 lazy loading：第一次请求加载 checkpoint，后续复用。两个独立 Uvicorn 进程都真实验证过重新加载。

# Chapter 14 Frontend

HTML 提供 textarea、Detect Entities 按钮、file input 和输出区域。JavaScript `fetch` 发送 HTTP request，等待 JSON，再用 `JSON.stringify(..., null, 2)` 显示。浏览器没有直接运行模型；它只与 FastAPI 通信。

生产系统还应做 HTML escaping、身份验证、文件大小限制、审计策略与 TLS。本教学版避免持久化输入，但这不等于完成合规审查。

# Chapter 15 File Upload

TXT 是 bytes，需按 UTF-8 decode。PDF 是页面容器，pypdf 只提取已有 text layer。扫描件只有图片，当前会得到空字符串并返回 400；OCR 是明确未实现的扩展。

文件扩展名检查是用户体验与基本过滤，不是完整安全边界。生产中还需 MIME sniffing、大小限制、超时、恶意 PDF 隔离。

# Chapter 16 Testing

测试分为 unit、integration、acceptance。15 个 pytest 覆盖 Tokenization、unknown、BIO、tensor shape、gradient、checkpoint、实体抽取、无实体、重复实体、API、TXT、PDF 与错误格式。真实结果为 15 passed；覆盖率 38%，低值主要因为 CLI main 与训练循环没有在 pytest 中重复跑，但它们已有真实执行日志。

手动五例全部通过。人工样例通过不等于总体性能通过；独立 test 指标与系统测试都必须保留。

# Chapter 17 Troubleshooting

`ModuleNotFoundError`：确认 VS Code interpreter 为 `.venv`，用 `uv sync --all-groups`。Shape mismatch：打印 input/logits shape，确认 num_labels 与 checkpoint 一致。Checkpoint missing：先训练或确认 `models/best_model.pt`。422：JSON 必须含非空 `text`。PDF 400：确认不是扫描件。端口占用：换 `--port 8001`。训练慢：本机是 CPU build；减少 batch/epochs 仅用于调试，正式结果需重新记录。

如果 validation loss 上升而 train loss 降低，通常是过拟合。不要查看 test label 后修改模型；先用 validation 分析。

# Chapter 18 Git 与 GitHub

先执行 `git status`、`git add`、`git commit`。检查 `.gitignore`，决定是否提交 573 KB checkpoint。公开前检查数据许可证、个人信息、secret 与大文件限制。用户没有授权，本项目未自动创建远程仓库或 push。

README 必须让陌生人能够安装、训练、评估、启动与测试。Tag 一个验收版本有助于 PDF 与代码一致，例如 `git tag v1.0-validated`，但发布前需用户自行审核。

# Chapter 19 Interview Preparation

5-10 分钟结构：1 分钟问题与隐私动机；1 分钟 BIO 数据；2 分钟 Embedding+BiLSTM；1 分钟训练与 word dropout；1 分钟 entity F1；1 分钟 Web demo；1 分钟失败实验与限制；最后提出真实标注数据、character encoder 或 CRF 改进。

以下每题依次给出简单中文、技术中文、英文面试回答。

1. What is NER? 简：找出文本中的人名地点机构。技：token-level sequence labeling 并合并 BIO spans。EN: NER assigns BIO labels to tokens and reconstructs typed entity spans.
2. Why BiLSTM? 简：同时看左右文。技：双向 hidden states 给每个 token 双侧上下文。EN: A BiLSTM encodes both left and right context for every token.
3. RNN vs LSTM? 简：LSTM 更能记长距离。技：gates 缓解普通 RNN 梯度消失。EN: LSTM gates preserve useful information and mitigate vanishing gradients.
4. Embedding? 简：把 ID 变成可学习向量。技：lookup table shape vocab x 64。EN: The embedding is a trainable lookup table mapping token IDs to 64-dimensional vectors.
5. BIO? 简：标记实体开始和内部。技：B/I/O 恢复多词边界。EN: BIO distinguishes entity beginnings, continuations, and outside tokens.
6. How learn? 简：不断降低错误。技：cross entropy, backpropagation, Adam。EN: The model minimizes cross-entropy through backpropagation and Adam updates.
7. Backpropagation? 简：从错误反推参数责任。技：链式法则计算 gradient。EN: Backpropagation applies the chain rule to compute parameter gradients.
8. Why validation? 简：选模型又不污染测试。技：validation F1 选 checkpoint。EN: Validation selects the checkpoint without tuning on the test set.
9. Prevent overfitting? 简：dropout 和独立验证。技：embedding dropout、ordinary word dropout、best checkpoint。EN: I used dropout, word masking, and validation-based checkpointing.
10. Why recall? 简：漏掉姓名风险高。技：FN 可能暴露隐私。EN: Recall matters because a false negative may expose personal information.
11. Unseen names? 简：看上下文和大小写。技：UNK + casing features + word dropout。EN: Unknown names share UNK embeddings but retain casing and contextual signals.
12. Unknown word? 简：映射 `<UNK>`。技：ID 1 进入已训练 unknown embedding。EN: It maps to the trained UNK embedding while casing features remain available.
13. Why ML? 简：参数从数据学习。技：141,232 参数经 gradient 更新。EN: It is ML because trainable parameters are optimized from labeled examples.
14. Train yourself? 简：是。技：自定义 nn.Module，四轮真实训练。EN: Yes, I defined and trained the PyTorch architecture myself.
15. Limitations? 简：合成模板不等于真实世界。技：domain shift、OOV、无 CRF、无 OCR。EN: The main limitation is synthetic template data and unvalidated real-world domain shift.
16. Softmax? 简：把分数转概率。技：训练 loss 内部完成。EN: Softmax normalizes logits, and cross-entropy applies it internally.
17. Logit? 简：未归一化类别分数。技：shape batch x seq x labels。EN: A logit is an unnormalized class score for each token.
18. Cross entropy? 简：惩罚正确类概率低。技：比较 logits 与 gold ID。EN: Cross-entropy penalizes low scores for the gold label.
19. Optimizer? 简：按 gradient 更新参数。技：本项目 Adam lr .003。EN: Adam updates parameters using adaptive gradient statistics at learning rate 0.003.
20. zero_grad? 简：清除上次梯度。技：PyTorch 默认累积。EN: Gradients accumulate by default, so I clear them before each batch.
21. Batch? 简：一次处理多句。技：padding 到 batch 最大长度。EN: A batch groups sentences and pads them to a common length.
22. Padding? 简：补齐不同长度。技：ID 0，loss ignore。EN: Padding aligns sequence lengths and is excluded from loss and metrics.
23. Mask? 简：标出真实 token。技：评估裁掉 padding。EN: The mask identifies real tokens so padding is excluded from evaluation.
24. Entity-level F1? 简：整个实体边界和类型都要对。技：exact span micro F1。EN: Entity F1 requires exact boundary and type matches.
25. Token accuracy weakness? 简：O 太多会虚高。技：不能反映完整 span。EN: Token accuracy can be inflated by the dominant O class.
26. Bidirectional output size? 简：两方向拼接。技：96+96=192。EN: Two 96-dimensional directions concatenate into 192 features.
27. forward input? 简：IDs 和 features。技：shapes `(B,L)` 与 `(B,L,4)`。EN: Forward receives token IDs and four casing features per token.
28. forward return? 简：每 token 的类别分数。技：`(B,L,8)` logits。EN: It returns logits shaped batch by length by eight labels.
29. model.eval? 简：切到推理模式。技：关闭 dropout。EN: Eval mode disables dropout for deterministic inference.
30. no_grad? 简：不保存训练图。技：降低内存和开销。EN: no_grad avoids autograd graph construction during inference.
31. Save more than weights? 简：推理还需词表配置。技：保存 vocab/labels/config/seed。EN: I save vocabulary, labels, architecture, preprocessing, seed, and weights.
32. Data leakage? 简：测试信息进入训练。技：句子与实体池隔离。EN: Leakage occurs when test information influences training; I check split intersections.
33. Perfect test score concern? 简：数据可能太简单。技：模板共享降低难度。EN: The perfect score is limited to a synthetic template distribution and is not a production claim.
34. Why not CRF? 简：先保持可理解。技：当前 Linear 已满足教学验收。EN: I avoided CRF complexity because the simpler classifier met the scoped learning goal.
35. CRF benefit? 简：学习标签转移。技：可减少非法 BIO。EN: A CRF can model tag-transition constraints and reduce invalid BIO sequences.
36. Redaction mechanism? 简：按模型 span 替换。技：扫描 token index 跳过实体区间。EN: Redaction replaces predicted spans and skips their covered token indices.
37. PDF support? 简：提取文字后送同一模型。技：pypdf 不做 NER。EN: pypdf extracts text; my trained model still performs all NER predictions.
38. Scanned PDF? 简：当前不支持。技：没有 OCR text layer。EN: Scanned PDFs need OCR, which is explicitly outside the current scope.
39. API validation? 简：Pydantic 检查输入。技：空 text 422，坏文件 400/415。EN: Pydantic validates JSON, and file errors return explicit HTTP status codes.
40. Next improvement? 简：真实人工标注数据。技：文档级盲测、character encoder、CRF。EN: My first improvement would be a real annotated blind set, then character features and possibly a CRF.

# Chapter 20 Complete Project Review

从零复现顺序：安装环境 -> 生成并检查数据 -> 理解 tensor -> 训练 -> 只用 validation 选 checkpoint -> 独立 test -> 手动测试 -> pytest -> Uvicorn -> 文件上传 -> 阅读报告。每一步失败都应先保存 evidence，再修复，不要只追求漂亮指标。

最终状态：功能验收通过；合成测试性能目标通过；扫描 PDF OCR 未实现；GitHub 未发布；真实生产域与真实初学者试读未验证。能够在面试中最有说服力的不是“1.0 F1”，而是解释首轮失败、如何诊断 OOV 过拟合、为什么改用 word dropout，以及为什么仍诚实限制结论。

# Appendix A 代码阅读指南

PDF 生成脚本会把最终 `.py`、HTML 内嵌代码和配置文件逐行附在后续页面。阅读顺序建议：constants -> preprocessing -> generate_data -> dataset -> model -> metrics -> train -> evaluate -> predict -> redact -> app -> tests。

# Appendix B 环境与依赖

实际环境、版本与未验证环境见本项目 ENVIRONMENT_REPORT。依赖真相来源是 `uv.lock`；requirements.txt 是导出副本。

# Appendix C 实验结果

四轮实验原始 JSON 全部保留。不要只展示最终成功：基线 0.1976、word dropout 0.6494、扩展数据 0.8681、最终 ordinary word dropout 0.9685 validation F1，构成完整工程推理链。

# Appendix D 验收报告

15/15 pytest、两次 Uvicorn 重启、五条手动样例、TXT/PDF 均已真实执行。详细证据见 ACCEPTANCE_REPORT。

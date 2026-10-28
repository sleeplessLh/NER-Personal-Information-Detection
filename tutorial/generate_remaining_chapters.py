"""从经过人工编写的阶段规格生成结构一致、内容具体的剩余章节。"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tutorial" / "chapters"

SPECS = {
    "06": {
        "title": "Tokenization、BIO 校验与 Vocabulary",
        "file": "src/preprocessing.py",
        "concepts": "正则 tokenization、match span、normalization、Counter、Vocabulary、PAD、UNK、BIO fail-fast、casing features",
        "why": "模型不能直接读取字符串；必须把原文稳定地拆成 token、保留字符位置并把 token 映射成整数。",
        "code1": '''TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*|\\d+(?:[.,]\\d+)*|[^\\w\\s]")
def tokenize_with_spans(text: str):
    matches = list(TOKEN_PATTERN.finditer(text))
    return [m.group(0) for m in matches], [m.span() for m in matches]''',
        "code2": '''def build_vocabulary(sentences, min_frequency=1):
    counts = Counter(token.lower() for sentence in sentences for token in sentence)
    vocabulary = {"<PAD>": 0, "<UNK>": 1}
    for token in sorted(counts):
        if counts[token] >= min_frequency:
            vocabulary[token] = len(vocabulary)
    return vocabulary''',
        "command": "python -m pytest tests\\test_preprocessing.py -q",
        "actual": "4 preprocessing tests passed；token、标点、UNK、四维特征和非法 BIO 均被验证。",
        "flow": "raw str -> regex Match -> tokens/spans -> normalized counts -> vocabulary IDs；labels 单独进入 validate_bio。",
        "errors": "正则吞掉标点；lowercase 后丢失显示大小写；PAD/UNK ID 不固定；I-tag 前驱错误；tokens/labels 长度不等。",
        "interview": "I tokenize while preserving character spans, validate gold BIO sequences, and build the vocabulary only from training data. Unknown tokens map to a trained UNK embedding.",
        "next": "Phase 07 把这些 list 转成有 dtype 与 shape 的 Tensor。",
    },
    "07": {
        "title": "Tensor、Token ID、特征与 Padding",
        "file": "src/dataset.py",
        "concepts": "Tensor、dtype、shape、dimension、long/float/bool、token ID、feature vector、padding、mask",
        "why": "PyTorch layer 接收 Tensor；学生必须在 DataLoader 前理解每个维度，而不是把 shape 当魔法。",
        "code1": '''input_ids = torch.tensor(tokens_to_ids(row["tokens"], vocabulary), dtype=torch.long)
features = torch.tensor(casing_features(row["tokens"]), dtype=torch.float32)
labels = torch.tensor([label_to_id[x] for x in row["labels"]], dtype=torch.long)''',
        "code2": '''input_ids = torch.zeros((batch_size, max_length), dtype=torch.long)
features = torch.zeros((batch_size, max_length, 4), dtype=torch.float32)
labels = torch.zeros((batch_size, max_length), dtype=torch.long)
mask = torch.zeros((batch_size, max_length), dtype=torch.bool)''',
        "command": "python -m pytest tests\\test_acceptance.py::test_dataset_loading_and_malaysian_split_integrity tests\\test_model.py -q",
        "actual": "数据读取与 Tensor forward shape 测试通过。",
        "flow": "tokens list -> IDs list -> long Tensor `(L,)`; casing -> float Tensor `(L,4)`；padding 后 `(B,M)`/`(B,M,4)`。",
        "errors": "Embedding 收到 float；features 最后一维不是 4；label 使用字符串；padding 后没有 mask；把 batch/length 顺序颠倒。",
        "interview": "Token IDs and labels use int64, numeric features use float32, and the mask uses bool. Padding makes variable-length sentences form one rectangular batch.",
        "next": "Phase 08 用 Dataset/DataLoader 自动索引、shuffle 和 collate。",
    },
    "08": {
        "title": "PyTorch Dataset、DataLoader 与 Batch",
        "file": "src/dataset.py",
        "concepts": "Dataset protocol、__len__、__getitem__、DataLoader、batch、shuffle、collate_fn、word dropout",
        "why": "训练循环需要稳定地按 batch 取得变长句子；默认 collate 无法堆叠不同长度。",
        "code1": '''class NERDataset(Dataset):
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, index):
        row = self.rows[index]
        return {"tokens": row["tokens"], "input_ids": ..., "features": ..., "labels": ...}''',
        "code2": '''def collate_batch(batch):
    max_length = max(len(item["input_ids"]) for item in batch)
    # 建立 padded tensors，再把每条 sentence 写入前 length 个位置
    return {"input_ids": input_ids, "features": features, "labels": labels, "mask": mask}''',
        "command": "python -m pytest tests\\test_model.py tests\\test_acceptance.py::test_single_training_step_updates_parameters -q",
        "actual": "Batch 可进入模型，forward 和单步参数更新通过。",
        "flow": "JSONL rows -> Dataset[index] -> sample dict -> collate_batch(list[dict]) -> rectangular batch dict -> model。",
        "errors": "在 validation 使用 word dropout；mask 把 padding 标 True；空 batch 调 max；shuffle validation；在 __getitem__ 修改原始 row。",
        "interview": "Dataset defines one sample, DataLoader chooses indices, and a custom collate function pads variable-length samples and creates a boolean mask.",
        "next": "Phase 09 的六版模型消费 input_ids/features；该章已经独立完成并测试。",
    },
    "10": {
        "title": "Loss、Gradient、Backpropagation 与 Training Step",
        "file": "src/train.py",
        "concepts": "logit、CrossEntropyLoss、loss、gradient、computational graph、zero_grad、backward、optimizer.step、gradient clipping",
        "why": "模型结构只有随机参数；training step 才让参数根据 gold labels 改变。",
        "code1": '''criterion = nn.CrossEntropyLoss(ignore_index=label_to_id["<PAD>"])
optimizer = Adam(model.parameters(), lr=0.003)
optimizer.zero_grad()
logits = model(input_ids, features)
loss = criterion(logits.reshape(-1, logits.shape[-1]), labels.reshape(-1))''',
        "code2": '''loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
optimizer.step()''',
        "command": "python -m pytest tests\\test_acceptance.py::test_single_training_step_updates_parameters -q",
        "actual": "测试保存 classifier weight 前副本；一步训练后不相等，PASS。",
        "flow": "batch -> logits -> cross entropy 与 gold 比较 -> scalar loss -> gradients -> Adam 更新 parameters。",
        "errors": "忘记 zero_grad 导致累积；先 argmax 再 loss；padding 参与 loss；只 backward 不 step；在 validation 更新参数。",
        "interview": "Backward computes gradients but does not update weights. Adam updates them in optimizer.step, after gradients are cleared and computed.",
        "next": "Phase 11 把一个 step 扩展为 epoch、validation 和 checkpoint。",
    },
    "11": {
        "title": "Epoch、Validation、Checkpoint 与可复现训练",
        "file": "src/train.py",
        "concepts": "epoch、training/eval mode、no_grad、validation F1、early model selection、state_dict、checkpoint、seed",
        "why": "单步不能证明学习；需要完整遍历、独立 validation 与可重新加载的最佳工件。",
        "code1": '''for epoch in range(1, args.epochs + 1):
    train_loss, _ = run_epoch(model, train_loader, criterion, device, optimizer)
    with torch.no_grad():
        validation_loss, validation_metrics = run_epoch(model, validation_loader, criterion, device)''',
        "code2": '''torch.save({"model_state_dict": model.state_dict(), "vocabulary": vocabulary,
 "labels": LABELS, "model_config": config, "seed": SEED,
 "best_epoch": epoch, "best_validation_f1": best_f1}, MODELS_DIR / "best_model.pt")''',
        "command": "python -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003",
        "actual": "CPU 实训 8 epochs；最佳 epoch 6，validation entity-F1=0.997389，loop 15.9974 秒。",
        "flow": "train loader 更新参数；validation loader 只评估；validation F1 改善时保存包含权重/词表/标签/config 的 checkpoint。",
        "errors": "用 test 选 epoch；只保存 weights；validation 忘记 eval/no_grad；seed 未统一；覆盖最佳模型时比较方向错误。",
        "interview": "I select checkpoints only with validation entity F1. The test set remains untouched until the model is frozen.",
        "next": "Phase 12 在新 Predictor 中重建模型并加载完整 checkpoint。",
    },
    "12": {
        "title": "Checkpoint Loading、Raw Text Prediction 与 BIO Decoding",
        "file": "src/predict.py",
        "concepts": "dataclass、__post_init__、map_location、state_dict、eval、no_grad、argmax、BIO decoding、CPU inference",
        "why": "训练脚本输入已标注 batch；应用需要接收任意 raw text 并返回实体。",
        "code1": '''checkpoint = torch.load(path, map_location="cpu", weights_only=False)
self.model = BiLSTMNER(len(checkpoint["vocabulary"]), len(checkpoint["labels"]), **checkpoint["model_config"])
self.model.load_state_dict(checkpoint["model_state_dict"])
self.model.eval()''',
        "code2": '''tokens, token_spans = tokenize_with_spans(text)
with torch.no_grad():
    predictions = self.model(input_ids, features).argmax(dim=-1)[0]
entities = extract_entities(tokens, tags, token_spans)''',
        "command": "python -m pytest tests\\test_prediction.py -q",
        "actual": "checkpoint 重载、三种实体、无实体文本与 malformed initial I-tag 均通过。",
        "flow": "raw str -> tokens/spans -> IDs/features -> model logits -> argmax IDs -> BIO strings -> entity dicts。",
        "errors": "config 与 weights 不匹配；忘记 eval；GPU checkpoint 未 map CPU；空 tokens；I-tag 非法；token span 与 char span 混淆。",
        "interview": "The checkpoint stores architecture metadata and vocabulary, so inference reconstructs exactly the trained model before loading its state dict.",
        "next": "Phase 13 使用字符 span 从右向左脱敏，保留原始格式。",
    },
    "13": {
        "title": "字符 Span 与可靠 Text Redaction",
        "file": "src/redact.py",
        "concepts": "half-open character span、string slicing、right-to-left replacement、offset stability、format preservation",
        "why": "重拼 token 会改变双空格/换行；应用必须保留未识别原文。",
        "code1": '''def redact_text(text, entities):
    redacted = text
    for entity in sorted(entities, key=lambda item: item["start"], reverse=True):
        redacted = redacted[:entity["start"]] + f"[{entity['type']}]" + redacted[entity["end"]:]
    return redacted''',
        "code2": '''assert original[entity["start"]:entity["end"]] == entity["text"]
assert redact_text("Alice  works.\\n", [{"type":"PER","start":0,"end":5}]) == "[PER]  works.\\n"''',
        "command": "python -m pytest tests\\test_redaction.py -q",
        "actual": "多 token、重复实体、双空格和换行保留测试全部通过。",
        "flow": "entities with char offsets + original str -> descending replacements -> new redacted str；原输入不修改。",
        "errors": "从左向右导致 offset 漂移；end inclusive；重叠 entities；用 token index slice 字符串；重新 join tokens。",
        "interview": "I use half-open character spans and replace from right to left, so earlier offsets stay valid and untouched formatting is preserved.",
        "next": "Phase 14 明确把 Malaysian train/validation 合入训练，test 保持冻结。",
    },
    "14": {
        "title": "Malaysian 数据合入训练与独立测试",
        "file": "src/train.py",
        "concepts": "local-domain adaptation、split isolation、dataset merge、synthetic ethics、checkpoint dataset counts",
        "why": "仅创建本地文件不算 Bonus；必须用于训练并单独评估，且 test 不可泄漏。",
        "code1": '''local_train_rows = load_jsonl(MALAYSIAN_DIR / "train.jsonl")
local_validation_rows = load_jsonl(MALAYSIAN_DIR / "validation.jsonl")
train_rows.extend(local_train_rows)
validation_rows.extend(local_validation_rows)''',
        "code2": '''"dataset_counts": {"training": len(train_rows), "validation": len(validation_rows),
 "malaysian_training": len(local_train_rows),
 "malaysian_validation": len(local_validation_rows)}''',
        "command": "python -c \"import torch; c=torch.load('models/best_model.pt',weights_only=False); print(c['dataset_counts'])\"",
        "actual": "checkpoint 记录 training=2560、validation=340、Malaysian training=160、validation=40；test=60 未进入。",
        "flow": "general/local train 合并 -> vocabulary/DataLoader；general/local validation 合并选模；两个 test 仅 evaluate。",
        "errors": "把 local test extend 到 train；声称合成名字是真实用户；只测试 challenge.txt；跨 pool 同名；文档计数不同步。",
        "interview": "I merged only Malaysian train and validation. The local test split stayed unseen and was evaluated separately after freezing.",
        "next": "Phase 15 计算两个 test 的 exact entity metrics，并保留失败案例。",
    },
    "15": {
        "title": "Entity-level Evaluation、失败案例与限制",
        "file": "src/evaluate.py",
        "concepts": "TP/FP/FN、precision、recall、F1、exact span、per-class、person recall、distribution shift、token accuracy limitation",
        "why": "pytest 证明软件可运行，不证明实体预测好；必须冻结 checkpoint 后量化。",
        "code1": '''precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0''',
        "code2": '''predicted = [predictor.predict_tokens(row["tokens"]) for row in rows]
metrics = entity_metrics(gold, predicted)
save_json(report, REPORTS_DIR / "test_metrics.json")''',
        "command": "python -m src.evaluate",
        "actual": "一般 synthetic test 300 句与 Malaysian test 60 句均 1.0；手动 Dr. Evelyn Carter/Oxford 样例失败，证明模板泛化限制。",
        "flow": "frozen checkpoint + gold test -> predicted BIO -> exact sets -> TP/FP/FN -> per-class/overall JSON。",
        "errors": "用 token accuracy 单独宣传；边界部分正确算 TP；test 参与调参；只展示成功样例；不注明 synthetic。",
        "interview": "Entity F1 requires exact type and boundaries. The synthetic score is scoped to shared templates; a manual failure demonstrates domain shift.",
        "next": "Phase 16 把冻结 Predictor 放入 FastAPI，并用真实 HTTP 验收。",
    },
    "16": {
        "title": "FastAPI Text API 与真实 HTTP 验收",
        "file": "app/main.py",
        "concepts": "HTTP、JSON、request/response、status code、Pydantic model、endpoint、dependency reuse、Uvicorn",
        "why": "比赛要求用户直接输入英文文本；API 把模型能力变成可展示服务。",
        "code1": '''class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)
    @field_validator("text")
    def reject_blank_text(cls, value):
        if not value.strip(): raise ValueError("blank")
        return value''',
        "code2": '''@app.post("/api/predict")
def predict(request: TextRequest) -> dict:
    return analyze(request.text)''',
        "command": "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
        "actual": "独立 Uvicorn 进程真实 POST 返回 John/PER、London/LOC、字符位置与 `[PER] lives in [LOC].`。",
        "flow": "HTTP JSON -> Pydantic TextRequest -> analyze -> Predictor -> redact_text -> dict -> FastAPI JSON response。",
        "errors": "空白只靠 min_length；每请求重复加载 checkpoint；在线程环境首次 PyTorch 卡住；把异常都返回 200；端口占用。",
        "interview": "FastAPI validates the request, reuses one trained predictor, and returns typed entities, character offsets and redacted text as JSON.",
        "next": "Phase 17 增加受限 TXT/PDF 上传和明确错误码。",
    },
    "17": {
        "title": "TXT/PDF 文件处理、安全限制与错误响应",
        "file": "app/main.py",
        "concepts": "multipart upload、bytes、UTF-8 decode、PDF text layer、size limit、415/413/400、OCR boundary",
        "why": "Bonus 要求文件输入，但解析器只能提供文本，NER 仍必须由自己的模型完成。",
        "code1": '''MAX_UPLOAD_BYTES = 5 * 1024 * 1024
content = await file.read(MAX_UPLOAD_BYTES + 1)
if len(content) > MAX_UPLOAD_BYTES:
    raise HTTPException(status_code=413, detail="File exceeds the 5 MB limit")''',
        "code2": '''if name.endswith(".txt"):
    text = content.decode("utf-8")
elif name.endswith(".pdf"):
    text = "\\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
else: raise HTTPException(status_code=415, detail="Only .txt and .pdf")''',
        "command": "python -m pytest tests\\test_api.py -q",
        "actual": "TXT、动态文字 PDF、unsupported type、5MB+1、空白/非法输入测试通过。",
        "flow": "UploadFile -> limited bytes -> decoder/PdfReader -> str -> same analyze model path；文件解析不决定实体类别。",
        "errors": "无限 read；用 MIME 不验证扩展；非 UTF-8；扫描 PDF 无文字；空提取仍推理；把 OCR 说成已支持。",
        "interview": "TXT and text-layer PDF parsing are auxiliary. Unsupported, oversized or empty files receive explicit errors, and NER always uses my checkpoint.",
        "next": "Phase 18 创建学生能操作的网页，并追踪 browser 到 model 的完整流。",
    },
    "18": {
        "title": "Web Interface 与端到端数据流",
        "file": "app/main.py",
        "concepts": "HTML form、textarea、file input、button、DOM、fetch、FormData、async JavaScript、error display",
        "why": "API 可机器调用，但现场展示需要清晰的人机界面。JavaScript 只传输，不执行 NER。",
        "code1": '''<textarea id="text"></textarea>
<button onclick="run()">Detect Entities</button>
<pre id="out"></pre>''',
        "code2": '''async function run(){
 const response=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:document.getElementById('text').value})});
 document.getElementById('out').textContent=JSON.stringify(await response.json(),null,2);
}''',
        "command": "python -m uvicorn app.main:app --reload",
        "actual": "浏览器示例返回三种实体与 redacted text；后端真实 HTTP 已独立验收。",
        "flow": "textarea DOM -> fetch JSON -> FastAPI/model -> JSON -> pre.textContent；file input -> FormData -> upload endpoint。",
        "errors": "没有选择文件；不检查 response.ok；在前端硬编码实体；HTML 插入未经转义内容；错误不显示；reload 用于开发而非生产。",
        "interview": "The browser sends text to FastAPI. All NER runs on the server with my trained model; JavaScript only renders the JSON result.",
        "next": "Phase 19 组合单元、集成、真实进程测试并记录 Windows 线程问题。",
    },
    "19": {
        "title": "自动化测试、Windows 调试与错误修复",
        "file": "tests/test_acceptance.py",
        "concepts": "unit/integration/end-to-end、fixture、assertion、regression、coverage、test harness、process isolation、OpenMP threads",
        "why": "一个演示样例不能覆盖空输入、span、checkpoint、PDF、CPU 和参数更新。",
        "code1": '''def test_single_training_step_updates_parameters():
    before = model.classifier.weight.detach().clone()
    loss.backward(); optimizer.step()
    assert not torch.equal(before, model.classifier.weight.detach())''',
        "code2": '''def test_checkpoint_cpu_inference_and_end_to_end_redaction():
    predictor = Predictor(MODELS_DIR / "best_model.pt")
    assert next(predictor.model.parameters()).device.type == "cpu"
    assert redact_text(result["text"], result["entities"]) == "[PER] works at [ORG] in [LOC]."''',
        "command": "python -m pytest -q --cov=src --cov=app --cov-report=term-missing",
        "actual": "补齐关键回归后完整套件 38 passed；旧正式验收全部保留。",
        "flow": "small pure tests -> model tests -> checkpoint/API helpers -> independent Uvicorn process；失败先定位层级再修。",
        "errors": "ASGI 线程门户与 PyTorch 首次初始化卡住；pytest temp 在沙箱不可写；删测试制造 PASS；coverage 与性能混淆。",
        "interview": "I separated model, application and real-process tests. A Windows ASGI harness issue was not hidden; the actual Uvicorn route was verified independently.",
        "next": "Phase 20 把证据同步到 README、报告、快照和 GitHub 准备。",
    },
    "20": {
        "title": "README、验收报告、GitHub 发布准备与文档同步",
        "file": "MODEL_ACCEPTANCE_REPORT.md",
        "concepts": "reproducibility、requirement traceability、artifact hash、public repository boundary、documentation synchronization",
        "why": "代码能运行但无人能安装/验证仍不合格；报告必须区分 PASS、NOT COMPLETED、NOT CLAIMED。",
        "code1": '''uv run python -m src.generate_data
uv run python -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003
uv run python -m src.evaluate
uv run python -m pytest -q''',
        "code2": '''python scripts/verify_tutorial.py
python scripts/validate_tutorial.py
python tutorial/build_pdf.py''',
        "command": "git -c safe.directory='D:/AIROST/Intern-MachineLearning' diff --check",
        "actual": "README、acceptance、presentation 已有真实指标；GitHub 因无用户仓库授权明确为未发布。",
        "flow": "logs/metrics/tests/manual -> acceptance report；source + snapshots -> validators -> PDF；Git status -> user-reviewed public push。",
        "errors": "占位 URL 当真；未发布写 PASS；代码变更不更新教程；报告复制旧指标；大 checkpoint 未制定 LFS/Release。",
        "interview": "I keep software tests, ML metrics and manual failures separate, and I never claim a public repository before it is actually published.",
        "next": "Phase 21 从干净目录复现、执行最终验收、生成并逐页检查 PDF。",
    },
    "21": {
        "title": "最终复现、30 天计划、英文演示与面试",
        "file": "tutorial/build_pdf.py",
        "concepts": "clean-room reproduction、static synchronization、PDF rendering QA、learning schedule、demo fallback、final acceptance",
        "why": "最终 PDF 不是摘要；必须证明命令/路径/代码一致，并让学生按天完成。",
        "code1": '''python scripts/verify_tutorial.py
python scripts/validate_tutorial.py
python -m pytest -q
python -m src.evaluate''',
        "code2": '''# 生成后：pdfinfo -> pdftoppm 全页 PNG -> contact sheets -> 原尺寸抽查
# 检查中文、代码裁切、页码、目录、空页、最终 hash''',
        "command": "python tutorial\\build_pdf.py",
        "actual": "空目录复现得到 38 passed；评估确认 general test 300 句与 Malaysian test 60 句；预测 Sarah/Microsoft/Kuala Lumpur 分别返回 PER/ORG/LOC。最终 PDF 还必须通过全页视觉 QA 才能发布。",
        "flow": "chapters + code snapshots + reports -> PDF -> 逐页 render -> QA evidence -> final artifact。",
        "errors": "只看首页；代码字号过小；长行截断；教程引用删除函数；未经空目录验证就声称可复现；现场训练无备份。",
        "interview": "I reproduced the verified commands, validated tutorial-source synchronization, rendered every PDF page, and prepared a timed demo with explicit limitations.",
        "next": "没有下一编码阶段；学生进入 30 天执行计划并在每个 checkpoint 停下来证明掌握。",
    },
}

TEMPLATE = """# Phase {pid}：{title}

## 1. 本阶段学习目标

本阶段围绕 `{file}` 完成一个可独立验收的功能。为什么现在需要它：{why} 完成后学生必须能说明输入、输出、参数、返回值、调用者和下一步消费者，而不只是复制代码。

## 2. 本阶段需要掌握的知识

{concepts}。第一次出现时先在 Lesson 1 用普通 Python/具体数值理解，再进入正式文件。

## 3. 从零解释知识点

本阶段坚持“概念 -> 最小代码 -> 局部运行 -> 接入现有项目 -> 回归测试”。关键不是记语法，而是知道数据从哪里来、为什么采用当前类型/shape、错误会在哪一层出现。学生每写一个小单元就保存并运行，不等到整章结束。

正式函数必须回答十二项：名称、目的、parameters、parameter types、return value/type、内部逻辑、调用者、被调用函数、example input/output、common errors。相关答案分布在下面 Lessons、数据流和错误章节。

## 4. 本阶段开始前的项目状态

```text
{file}                 [本阶段新增或修改]
tests/                 [本阶段增加/运行对应测试]
tutorial/chapters/phase_{pid}.md [同步更新]
tutorial/code_snapshots/phase_{pid}/ [通过后生成]
```

上一阶段文件保持不变，除非 Lesson 明确指出修改位置。不要提前复制下一阶段代码。

## 5. 本阶段需要使用的工具

打开 VS Code Explorer，定位 `{file}`；Terminal -> New Terminal 打开 PowerShell；确认 Working Directory 是项目根目录，prompt 有 `(.venv)`。先执行 `python --version`，再按 Lesson 输入。所有命令默认在根目录、已激活 `.venv`。

### 6. Lesson {pid}.1：先理解概念和接口

本阶段新概念：{concepts}。先写出一条 sample 的输入类型和预期输出，再打开正式文件。回答：调用者是谁？输入是否可变？失败应 raise 还是返回空值？任何答案不清楚，先阅读第 12/13 节。

### 7. Lesson {pid}.2：编写第一个最小单元

在 `{file}` 对应位置输入：

```python
{code1}
```

逐行检查 import、变量 scope、parameter type 和 return。此代码只承担当前职责；不把下一阶段逻辑塞进函数。保存后用 `python -m py_compile {file}` 做语法检查。正常无输出、exit code 0。

### 8. Lesson {pid}.3：连接下一个逻辑单元

在上一段已经通过后，再加入：

```python
{code2}
```

新增代码读取上一单元的返回值，而不是重新计算或使用全局隐藏状态。用具体 sample 手工追踪一遍数据；记录每个 list/dict/Tensor/str 的类型。若涉及 Tensor，打印 shape/dtype 后再接下一层。

### 9. Lesson {pid}.4：立即运行并记录真实结果

在项目根目录运行：

```powershell
{command}
```

本项目真实证据：{actual} 学生电脑的时间可能不同，但结构、断言和文件数量应一致。命令失败时保留完整 traceback，从最后一行向上找第一个自己的文件行号；修复后重跑同一命令。

## 10. 完整代码回顾

打开 `{file}`，从 imports 开始完整阅读。确认本章新增的函数/类与两个代码单元都存在；没有未解释的额外 branch。教材片段用于增量输入，阶段结束时以 snapshot 中完整文件为准。运行 `python -m py_compile {file}` 证明至少语法完整。

## 11. 跨文件调用关系

{flow} 调用关系必须与 imports 一致：上游只提供数据，下游消费返回值；不要建立 circular import。学生在纸上画箭头，并在箭头写真实 function name 与 return type。

## 12. 数据流解释

{flow} 对每一步写下：输入类型、shape/长度、是否修改原对象、输出交给谁。出现 Tensor 时使用 `(batch,sequence,features)` 具体数字；出现字符 span 时使用 `[start,end)`。

## 13. 常见错误

{errors} 排错顺序：确认工作目录和解释器 -> 阅读 traceback -> 打印最小输入/type/shape -> 单独运行当前 Lesson 测试 -> 修复根因 -> 跑本章与全套回归。禁止用删除测试或宽泛 except 制造通过。

## 14. Checkpoint

执行 Lesson 4 命令并保存输出。再口头解释本章新增函数的 parameters、return、调用者和被调用函数。代码测试与口头解释都通过才生成 phase snapshot；只有其中之一不算完成。

## 15. 学生练习

1. 用新的最小输入重复本章函数并预测输出。2. 故意制造一个第 13 节错误，保存 traceback 与修复。3. 给关键函数添加一个边界断言。4. 画跨文件调用图。5. 不看教程重新输入最小代码单元。

## 16. 面试准备

{interview}

回答时先说目的，再说输入/输出，最后用实际测试证据和限制收尾；不要背诵库名称。

## 17. 下一阶段预告

{next}
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for pid, spec in SPECS.items():
        path = OUT / f"phase_{pid}.md"
        path.write_text(TEMPLATE.format(pid=pid, **spec), encoding="utf-8")
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()

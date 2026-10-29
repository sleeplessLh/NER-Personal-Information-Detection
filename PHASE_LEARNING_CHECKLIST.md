# PHASE LEARNING CHECKLIST

本清单用于客观决定是否可以进入下一 Phase。页码来自最终 141 页主教程。`PASS` 只表示工程/教学结构可验证，不代表真人学习实验。

**Independent Human Learning Test: NOT VERIFIED**

## 通用增量规则

每个 Phase 必须遵守：知识讲解 → 最小实验 → 增量代码 → 函数契约/逐逻辑单元解释 → 运行验证 → 阶段总结。修改已有文件时，先定位 class/function，再明确新增、替换或删除的代码；不得让学生自行比较两个大文件猜差异。

## Phase 00 — 项目边界与证据（PDF 第 9–12 页）

### Knowledge Check
能够区分 NER、脱敏、软件测试、ML 评估与人工展示。

### Coding Check
写出三类实体的输入/输出样例。

### Execution Check
```powershell
python --version; git status --short
```

### Expected Result
版本可见，Git 状态可解释。

### Common Errors
把合成结果说成真实数据；把 pytest 当性能证明。

### Completion Criteria
能口述范围、禁止捷径和完成证据。

### Function Contracts and File Relationships
无正式函数；本阶段定义后续所有文件的输入输出边界。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 01 — Windows/Python/VS Code/venv（PDF 第 13–24 页）

### Knowledge Check
理解解释器、PATH、venv、package。

### Coding Check
独立创建和重新激活 .venv，运行 hello_python。

### Execution Check
```powershell
python -m learning.hello_python
```

### Expected Result
解释器路径位于项目 .venv。

### Common Errors
ExecutionPolicy、选错 interpreter、在错误 cwd。

### Completion Criteria
新终端可重复运行且 uv pip check 通过。

### Function Contracts and File Relationships
describe_environment()：无输入，返回环境描述字符串；main() 调用并打印；由 python -m 调用。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 02 — Python 基础（PDF 第 25–28 页）

### Knowledge Check
理解 collection/function/class/self/inheritance/dataclass/type hint。

### Coding Check
独立写 list→dict 函数和 Entity 对象。

### Execution Check
```powershell
python -m learning.python_foundations
```

### Expected Result
标签计数和实体 dict 正确。

### Common Errors
缩进、变量 scope、忘记 self、半开区间错误。

### Completion Criteria
能改输入并预测输出，py_compile 通过。

### Function Contracts and File Relationships
count_labels(labels)->dict；NamedItem.__init__(name) 保存基类字段；Entity.__post_init__ 校验 span；as_dict()->dict；main() 组织演示。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 03 — NER 与 BIO（PDF 第 29 页）

### Knowledge Check
理解 token/entity/sequence/B-I-O。

### Coding Check
手工标注并实现校验与合并。

### Execution Check
```powershell
python -m learning.bio_demo
```

### Expected Result
合法 BIO 合并为实体，非法序列抛 ValueError。

### Common Errors
token/label 不等长、I 标签无前导 B。

### Completion Criteria
能解释多词实体边界。

### Function Contracts and File Relationships
validate_bio(tokens,labels)->None/raise；bio_to_entities(tokens,labels)->list[dict]，调用 validate_bio；main() 提供样例。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 04 — 项目骨架与 Git（PDF 第 30–34 页）

### Knowledge Check
理解 package、Path、配置集中化和 snapshot。

### Coding Check
创建目录、constants、gitignore。

### Execution Check
```powershell
python -m py_compile src/constants.py
```

### Expected Result
exit code 0，ROOT 正确。

### Common Errors
硬编码绝对路径、缺 __init__.py。

### Completion Criteria
从根目录可 import src.constants。

### Function Contracts and File Relationships
constants 无函数；向 generate/train/predict 提供共享 Path。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 05 — 数据生成（PDF 第 35–41 页）

### Knowledge Check
理解 JSONL、标注 schema、seed、split/leakage。

### Coding Check
生成两套数据且验证数量。

### Execution Check
```powershell
python -m src.generate_data
```

### Expected Result
general 2400/300/300；Malaysia 160/40/60。

### Common Errors
placeholder 错位、split 实体重叠、test 进入训练。

### Completion Criteria
数据可重复生成且 BIO 有效。

### Function Contracts and File Relationships
_annotate(rendered,values)->token/label row；generate_split/generate_malaysian_split(split,size,seed)->rows；_write_jsonl(rows,path) 写文件；main() 调用全部生成器。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 06 — Preprocessing/Vocabulary（PDF 第 42–46 页）

### Knowledge Check
理解 token span、normalize、PAD/UNK、casing。

### Coding Check
实现 preprocessing 全函数。

### Execution Check
```powershell
python -m pytest tests/test_preprocessing.py -q
```

### Expected Result
6 passed。

### Common Errors
正则 span 错、UNK KeyError、(L,4) 错。

### Completion Criteria
测试通过并能手算 token ids。

### Function Contracts and File Relationships
tokenize(text)->tokens；tokenize_with_spans(text)->tokens/spans；normalize_token(token)->str；validate_bio(...)；build_vocabulary(sentences,min_frequency)->dict；tokens_to_ids(...)->ids；casing_features(tokens)->(L,4) list；save_json/load_json 持久化。调用者为 data/dataset/train/predict。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 07 — Tensor 与 Padding（PDF 第 47–52 页）

### Knowledge Check
理解 dtype/shape/mask。

### Coding Check
构造 long/float/bool tensor 并断言。

### Execution Check
```powershell
python -m learning.tensor_demo
```

### Expected Result
打印 dtype 与预期 shape。

### Common Errors
Embedding 收到 float、标签维度错。

### Completion Criteria
能解释每个轴。

### Function Contracts and File Relationships
main() 构造一个样本并展示转换；后续 Dataset/Model 消费相同结构。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 08 — Dataset/DataLoader（PDF 第 53–55 页）

### Knowledge Check
理解 sample、batch、collate。

### Coding Check
实现 Dataset 和 padding。

### Execution Check
```powershell
python -m learning.dataloader_demo
```

### Expected Result
批次 shape 统一、mask 正确。

### Common Errors
未 padding 直接 stack、pad id 错。

### Completion Criteria
能追踪 row→sample→batch。

### Function Contracts and File Relationships
load_jsonl(path)->rows；NERDataset.__init__ 保存映射，__len__ 返回数量，__getitem__(index)->tensor dict；collate_batch(batch)->padded dict；demo main() 调用 DataLoader。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 09 — Embedding/LSTM/BiLSTM（PDF 第 56–70 页）

### Knowledge Check
理解 Module/Parameter/Embedding/双向上下文/logits。

### Coding Check
完成 V1→V6 与最终 model。

### Execution Check
```powershell
python -m pytest tests/test_model_versions.py tests/test_model.py -q
```

### Expected Result
7 passed，logits=(B,L,8)。

### Common Errors
Linear 输入维度、bidirectional 倍增、错误 softmax。

### Completion Criteria
能画 shape 流并解释每版变化。

### Function Contracts and File Relationships
BiLSTMNER.__init__(vocab_size,num_labels,embedding_dim,hidden_dim,dropout) 建层；forward(input_ids,features)->logits。由 train/predict 调用。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 10 — Loss 与 Backprop（PDF 第 71–73 页）

### Knowledge Check
理解 loss、gradient、optimizer 三者分工。

### Coding Check
独立完成一次 training step。

### Execution Check
```powershell
python -m learning.training_step_demo
```

### Expected Result
finite loss、参数已改变。

### Common Errors
漏 zero_grad/backward/step，标签越界。

### Completion Criteria
能逐句解释四个训练动作。

### Function Contracts and File Relationships
demo main() 构造 batch→model→loss→backward→clip→step，并比较权重；正式 run_epoch 复用同一顺序。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 11 — Epoch/Validation/Checkpoint（PDF 第 74–78 页）

### Knowledge Check
理解 train/eval/no_grad、validation 与 reproducibility。

### Coding Check
实现 run_epoch/main 并训练。

### Execution Check
```powershell
python -m src.train
```

### Expected Result
16 epochs，保存 best_model.pt 和 history。

### Common Errors
validation 更新参数、按 train loss 保存、漏 seed。

### Completion Criteria
checkpoint 五类内容齐全。

### Function Contracts and File Relationships
set_seed(seed)->None；run_epoch(model,loader,criterion,device,optimizer=None)->loss/pred/gold；main() 加载数据、建模型、循环、保存。metrics.bio_to_spans(labels)->set；entity_metrics(gold,pred)->dict。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 12 — Loading/Prediction/BIO decode（PDF 第 79–81 页）

### Knowledge Check
理解 CPU load、eval、argmax、offset。

### Coding Check
实现 Predictor 与 extract_entities。

### Execution Check
```powershell
python -c "from src.predict import Predictor; print(Predictor().predict('Ahmad Ali studies in Johor Bahru.'))"
```

### Expected Result
返回 entities 与字符 start/end。

### Common Errors
checkpoint config 不匹配、标点被实体吞入。

### Completion Criteria
PER/LOC/ORG 示例能识别。

### Function Contracts and File Relationships
Predictor.__post_init__ 重建模型；predict_tokens(tokens)->tags；predict(text)->result；extract_entities(tokens,tags,spans)->entities。API 调用 Predictor。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 13 — Text Redaction（PDF 第 82–85 页）

### Knowledge Check
理解 half-open span 与逆序替换。

### Coding Check
实现 token 与 char 两种脱敏。

### Execution Check
```powershell
python -m pytest tests/test_redaction.py -q
```

### Expected Result
3 passed，空格标点保留。

### Common Errors
正序替换导致 offset 漂移。

### Completion Criteria
重复实体、多行文本均正确。

### Function Contracts and File Relationships
redact_tokens(tokens,entities)->normalized text；redact_text(text,entities)->preserved text。API 使用后者。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 14 — Malaysian 数据（PDF 第 86–93 页）

### Knowledge Check
理解 domain focus、合成限制、独立 test。

### Coding Check
合并 train/validation，不接触 test。

### Execution Check
```powershell
python -m pytest tests/test_preprocessing.py -q -k disjoint
```

### Expected Result
泄漏测试通过。

### Common Errors
同名跨 split、模板泄漏、夸大真实性。

### Completion Criteria
checkpoint 记录数据数量。

### Function Contracts and File Relationships
复用 generate_malaysian_split 与 train.main；没有新预测捷径。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 15 — Entity-level Evaluation（PDF 第 94–97 页）

### Knowledge Check
理解 exact span TP/FP/FN、P/R/F1。

### Coding Check
实现 evaluate 并解读报告。

### Execution Check
```powershell
python -m src.evaluate
```

### Expected Result
两份 JSON 指标生成。

### Common Errors
只报 token accuracy、忽略 PER recall。

### Completion Criteria
能手算并解释限制。

### Function Contracts and File Relationships
evaluate.main() 加载 Predictor/数据并调用 entity_metrics；bio_to_spans 与 entity_metrics 的契约见 Phase 11。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 16 — FastAPI Text API（PDF 第 98–100 页）

### Knowledge Check
理解 HTTP/JSON/Pydantic/cache/status。

### Coding Check
实现文本预测与脱敏路由。

### Execution Check
```powershell
python -m pytest tests/test_text_api.py -q
```

### Expected Result
3 passed。

### Common Errors
422 body 错、每次请求重复加载模型。

### Completion Criteria
真实模型响应而非硬编码。

### Function Contracts and File Relationships
TextRequest validator 输入 str→str/raise；get_predictor()->缓存 Predictor；analyze(text)->预测 dict；predict/redact 路由调用 analyze。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 17 — TXT/PDF API（PDF 第 101–103 页）

### Knowledge Check
理解 upload bytes、类型/大小限制、text layer。

### Coding Check
实现上传分析。

### Execution Check
```powershell
python -m pytest tests/test_file_api.py -q
```

### Expected Result
TXT/PDF 与 400/413/415 测试通过。

### Common Errors
把扩展名当唯一验证、声称支持 OCR。

### Completion Criteria
所有文件最终进入同一 Predictor。

### Function Contracts and File Relationships
analyze_uploaded_content(name,content)->result/HTTPException；由 upload route 调用，内部调用 analyze。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 18 — Web Interface（PDF 第 104–109 页）

### Knowledge Check
理解 DOM/fetch/前后端数据流。

### Coding Check
实现 Input/Redact/Output/Clear。

### Execution Check
```powershell
python -m pytest tests/test_web_ui.py tests/test_api.py -q
```

### Expected Result
Web/API 测试通过。

### Common Errors
JS 关键词匹配、错误只进 console。

### Completion Criteria
真实浏览器可连续提交。

### Function Contracts and File Relationships
home()->HTML；predict/redact route；前端 submit handler 调 /api/redact。NER 只在后端 Predictor。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 19 — Testing/Debugging（PDF 第 110–120 页）

### Knowledge Check
理解 unit/integration/E2E 与 traceback。

### Coding Check
运行并定位单测失败。

### Execution Check
```powershell
python -m pytest -q
```

### Expected Result
56 passed。

### Common Errors
删测试、吞异常、错误 cwd/interpreter。

### Completion Criteria
单测与全套均通过。

### Function Contracts and File Relationships
pytest test_* 函数无生产调用者，由 pytest discovery 调用；fixture/parametrize 提供输入，assert 验证公开契约。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 20 — Documentation/GitHub（PDF 第 121–131 页）

### Knowledge Check
理解可复现证据、hash、限制披露。

### Coding Check
同步 README/报告/演示材料。

### Execution Check
```powershell
python scripts/validate_tutorial.py; python scripts/verify_tutorial.py
```

### Expected Result
22 phases、20 paths 通过。

### Common Errors
旧测试数、虚构 URL、遗漏限制。

### Completion Criteria
文档与源代码一致。

### Function Contracts and File Relationships
文档无运行时函数；作为安装、验收和展示入口，引用 train/evaluate/app/tests 的真实命令。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Phase 21 — Final Reproduction（PDF 第 132–141 页）

### Knowledge Check
理解 clean-room、render QA、证据边界。

### Coding Check
执行阶段式复现并记录反馈。

### Execution Check
```powershell
python scripts/student_reproduction_audit.py
```

### Expected Result
22/22 PASS。

### Common Errors
整包复制最终项目、把自动化当真人测试。

### Completion Criteria
工程复现通过且 Human Test 保持 NOT VERIFIED。

### Function Contracts and File Relationships
student_reproduction_audit.main() 按 PHASE_FILES 累积文件并运行 checkpoints；validators 检查章节结构/路径；QA 脚本检查 PDF。

### Edit Location Rule
打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。

## Audit Summary

- Phase coverage: 22/22。
- 页码覆盖：第 9–141 页。
- 自动化基线：56 tests。
- 模型架构保持：Embedding → BiLSTM → Linear token classifier。
- Independent Human Learning Test: NOT VERIFIED。

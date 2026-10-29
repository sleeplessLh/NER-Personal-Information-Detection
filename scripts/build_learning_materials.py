"""生成 30 天学习计划、Phase 验收清单、面试材料及学习计划 PDF。"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
PLAN_MD = ROOT / "NER_30_Day_Learning_Plan.md"
PLAN_PDF = ROOT / "output/pdf/NER_30_Day_Learning_Plan.pdf"
CHECKLIST_MD = ROOT / "PHASE_LEARNING_CHECKLIST.md"
INTERVIEW_MD = ROOT / "INTERVIEW_PREPARATION.md"

PHASE_PAGES = {
    0: "9–12", 1: "13–24", 2: "25–28", 3: "29", 4: "30–34", 5: "35–41",
    6: "42–46", 7: "47–52", 8: "53–55", 9: "56–70", 10: "71–73",
    11: "74–78", 12: "79–81", 13: "82–85", 14: "86–93", 15: "94–97",
    16: "98–100", 17: "101–103", 18: "104–109", 19: "110–120",
    20: "121–131", 21: "132–141",
}

# day, phase/page, knowledge, files, code, commands, output, completion, failure, hours
DAYS = [
    (1, "Phase 00，第 9–12 页", "项目目标、NER 输入/输出、PER/LOC/ORG、证据层级与禁止捷径。", "阅读 README.md；创建学习日志 learning_log.md（不改模型代码）。", "手写 3 个输入/实体/脱敏输出例子，并区分模型测试、软件测试和人工演示。", "git status --short; python --version", "显示 Python 版本；Git 工作树状态可解释。", "能独立说出项目边界、三类实体和为什么不能调用现成 NER API。", "若概念混淆，回到第 9–10 页逐项写输入、处理、输出；若 Git 报错，确认当前目录。", "3 小时"),
    (2, "Phase 01，第 13–18 页", "Windows PowerShell、PATH、VS Code、项目目录、虚拟环境。", "创建项目目录与 .venv；创建 learning/hello_python.py。", "跟敲 describe_environment()、main guard；不要复制后续文件。", "py -3.11 -m venv .venv; .\\.venv\\Scripts\\Activate.ps1; python -m learning.hello_python", "输出 Python 可执行文件位于项目 .venv，并显示 CPU 环境信息。", "关闭并重开 PowerShell 后仍能激活 .venv 并运行 hello_python。", "ExecutionPolicy 错误按第 15 页处理；python 指向系统环境时重新选择 VS Code interpreter。", "4 小时"),
    (3, "Phase 01，第 19–24 页", "pip/uv、requirements、包安装、import 与依赖检查。", "创建 requirements.txt、pyproject.toml；不创建模型文件。", "逐项理解依赖用途，安装后写三个 import 检查。", "python -m pip install uv; uv pip install --python .venv\\Scripts\\python.exe -r requirements.txt; uv pip check --python .venv\\Scripts\\python.exe", "All installed packages are compatible；torch/fastapi/pytest 可 import。", "能解释虚拟环境隔离什么，并在新终端验证解释器路径。", "下载失败检查网络与代理；Access denied 改用项目内 UV_CACHE_DIR；不要混用多个 Python。", "4–5 小时"),
    (4, "Phase 02，第 25–28 页", "list/dict/loop/function/class/self/inheritance/dataclass/type hint/半开区间。", "创建 learning/python_foundations.py。", "跟敲 count_labels、NamedItem、Entity、as_dict、main，并改变一个实体输入。", "python -m learning.python_foundations; python -m py_compile learning/python_foundations.py", "输出实体字典和标签计数；py_compile 无报错。", "能在不看答案时写一个接收 list[str]、返回 dict 的函数，并解释 self。", "NameError 查变量作用域；TypeError 查参数；缩进错误从 traceback 最后一行定位。", "4 小时"),
    (5, "Phase 03，第 29 页", "Token、Sequence、Entity、Label、BIO 边界与非法 I 标签。", "创建 learning/bio_demo.py。", "跟敲 validate_bio、bio_to_entities、main；手工设计一条多 Token ORG。", "python -m learning.bio_demo", "输出 PER/ORG/LOC 实体；故意非法 BIO 时抛出可读 ValueError。", "给任意短句手工写等长 token/label，并正确合并实体。", "token/label 数量不同先逐个编号；I-ORG 前没有 B-ORG 时修正标签。", "3–4 小时"),
    (6, "Phase 04，第 30–34 页", "Python package、绝对路径、配置常量、Git snapshot。", "创建 src/、app/、tests/、data/、models/、reports/；创建 src/__init__.py、src/constants.py、.gitignore。", "逐行跟敲 ROOT/DATA_DIR/MODELS_DIR 等 Path 常量并解释 __file__。", "python -m py_compile src/constants.py; python -c \"from src.constants import ROOT; print(ROOT)\"; git status --short", "ROOT 等于项目根目录；语法检查无输出。", "从项目根目录和子目录调用时都能说明路径为什么稳定。", "ModuleNotFoundError 检查是否在根目录；路径错误打印 Path.resolve()；不要硬编码用户名。", "3–4 小时"),
    (7, "Phase 05，第 35–38 页", "JSONL、sample schema、人工标注、随机种子、数据泄漏。", "创建 src/preprocessing.py 的 BIO 基础函数；创建 src/generate_data.py 前半部分。", "跟敲 _annotate、模板、实体池、generate_split；在纸上验证一个 span。", "python -m py_compile src/preprocessing.py src/generate_data.py", "命令无输出且 exit code 0。", "能解释 tokens 与 labels 为什么必须等长，以及 split 间实体池为何分离。", "KeyError 检查模板 placeholder；标签错位逐 token 打印；随机结果不同检查 seed。", "4–5 小时"),
    (8, "Phase 05，第 39–41 页", "Malaysian 合成数据、train/validation/test 隔离、重复检查与伦理限制。", "完成 src/generate_data.py；生成 data/processed 与 data/malaysian。", "跟敲 generate_malaysian_split、_write_jsonl、main 和泄漏 fail-fast。", "python -m src.generate_data; (Get-Content data\\processed\\train.jsonl | Measure-Object -Line).Lines", "生成 general 2400/300/300 与 Malaysian 160/40/60；示例命令输出 2400。", "文件数量、每行 JSON、BIO 长度和 split 不重叠均可检查。", "行数不是 2400 时检查 main 的 split size；JSONDecodeError 查看出错行；不要提前依赖 Phase 08 才创建的 src.dataset。", "4 小时"),
    (9, "Phase 06，第 42–46 页", "Tokenizer、字符 span、normalize、Vocabulary、PAD/UNK、casing features。", "完成 src/preprocessing.py；创建 tests/test_preprocessing.py。", "逐函数跟敲 tokenize_with_spans、build_vocabulary、tokens_to_ids、casing_features、save/load_json。", "python -m pytest tests/test_preprocessing.py -q", "6 个 preprocessing 测试通过。", "能说明每个函数输入/输出，并手算一个未知词得到 UNK id。", "span 错位检查正则 match.start/end；KeyError 检查是否使用 vocabulary.get；shape 应为 (L,4)。", "4–5 小时"),
    (10, "Phase 07，第 47–52 页", "Tensor、dtype、shape、Token ID、padding、mask。", "创建 learning/tensor_demo.py。", "跟敲 LongTensor/FloatTensor/BoolTensor 的构造和 shape 断言。", "python -m learning.tensor_demo", "输出 input_ids/labels 为 int64、features 为 float32、mask 为 bool 及对应 shape。", "能解释为什么 Embedding 输入不能是 float，以及 (L,4) 中两个维度含义。", "dtype 错误打印 tensor.dtype；shape 错误逐层打印；空序列先查 tokenization。", "4 小时"),
    (11, "Phase 08，第 53–55 页", "Dataset、__len__、__getitem__、DataLoader、collate_fn、batch padding。", "创建 src/dataset.py 与 learning/dataloader_demo.py。", "跟敲 load_jsonl、NERDataset 三个方法、collate_batch；观察两个不同长度样本。", "python -m learning.dataloader_demo", "输出 padded batch、mask 和统一的 (batch, max_length) shape。", "能从 row 追踪到 batch 中 input_ids/features/labels/mask。", "stack 报错通常是未 padding；padding id 混乱检查 constants；DataLoader 空检查数据路径。", "4–5 小时"),
    (12, "Phase 09，第 56–61 页", "Neural Network、Module、Layer、Parameter、Embedding。", "按顺序创建 tutorial/model_versions/model_v1.py 与 model_v2.py。", "只跟敲 V1/V2；比较新增的 __init__ 参数、super() 和 embedding 输出。", "python -m pytest tests/test_model_versions.py -q -k \"version_1 or version_2\"", "V1/V2 对应测试通过；Embedding shape 为 (batch,length,embedding_dim)。", "能说明 embedding table 哪些值会训练，以及 padding_idx 的作用。", "AttributeError 检查 super().__init__；索引越界检查 vocab_size；dtype 必须 long。", "4–5 小时"),
    (13, "Phase 09，第 61–65 页", "RNN 局限、LSTM gates、hidden state、双向上下文。", "创建 model_v3.py 与 model_v4.py。", "跟敲 BiLSTM、Linear、Dropout；画出 forward/backward 两条信息流。", "python -m pytest tests/test_model_versions.py -q -k \"version_3 or version_4\"", "V3/V4 测试通过；BiLSTM 最后一维为 2×hidden_dim。", "能比较 LSTM 与 BiLSTM，并解释为什么姓名识别需要左右文。", "维度不匹配检查 bidirectional=True 和 Linear 输入；Dropout 只在 train 模式随机。", "4–5 小时"),
    (14, "Phase 09，第 65–70 页", "forward 数据流、特征拼接、logits 与完整 shape tracking。", "创建 model_v5.py、model_v6.py；最终创建 src/model.py。", "逐版本跟敲 forward；明确 V5→V6 新增 features projection 与 cat。", "python -m pytest tests/test_model_versions.py tests/test_model.py -q", "7 个模型相关测试通过；最终 logits shape=(batch,length,8)。", "不看代码画出 input_ids/features→embedding→BiLSTM→Linear→logits。", "matmul shape 错误按每层打印 shape；num_labels 应与标签映射一致；不要加 softmax。", "5 小时"),
    (15, "Phase 10，第 71–73 页", "CrossEntropyLoss、gradient、zero_grad、backward、optimizer.step、gradient clipping。", "创建 learning/training_step_demo.py。", "跟敲一次完整训练 step，并在 step 前后复制 classifier 权重比较。", "python -m learning.training_step_demo", "输出 finite loss、logits (1,4,8)，并确认 classifier changed=True。", "能准确区分 backward 计算梯度与 step 更新参数。", "loss nan 检查标签范围；参数不变检查是否漏 step；梯度累积检查是否漏 zero_grad。", "4–5 小时"),
    (16, "Phase 11，第 74–78 页", "Epoch、train/eval、no_grad、validation、checkpoint、随机种子。", "创建 src/metrics.py 与 src/train.py；创建 models/、reports/ 输出目录。", "先跟敲 set_seed 和 run_epoch，再跟敲 main；标出 optimizer=None 的 validation 分支。", "python -m py_compile src/train.py src/metrics.py; python -m src.train", "CPU 完成 16 epochs；生成 models/best_model.pt、vocabulary.json、labels.json、config.json、training_history.json。", "能打开 history 说明 train/validation loss，并解释为何按 validation 保存。", "训练慢确认 CPU 正常；找不到数据先运行 generate_data；OOM 降低 batch 而不改模型定义。", "5 小时（可让训练继续运行）"),
    (17, "Phase 12，第 79–81 页", "map_location、eval/no_grad、argmax、BIO decoding、字符 offset。", "创建 src/predict.py。", "跟敲 Predictor.__post_init__、predict_tokens、predict、extract_entities。", "python -c \"from src.predict import Predictor; print(Predictor().predict('Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.'))\"", "返回 text/tokens/tags/entities；实体包含 text/type/start/end。", "能追踪 raw text→tokens→ids→logits→tags→entities。", "checkpoint key 错误核对保存结构；CPU load 使用 map_location；标点被吞检查标点 tag 归 O。", "4–5 小时"),
    (18, "Phase 13，第 82–85 页", "半开字符区间、从右向左替换、保留空格/标点/换行。", "创建 src/redact.py 与 tests/test_redaction.py。", "跟敲 redact_tokens 和 redact_text；先在纸上演算两个 span 的正序/逆序差异。", "python -m pytest tests/test_redaction.py -q", "3 个脱敏测试通过；原文非实体内容保持不变。", "能解释为什么字符替换必须从最大 start 向左进行。", "位置漂移检查排序 reverse=True；空格变化使用 redact_text 而不是重新 join token。", "3–4 小时"),
    (19, "Phase 14，第 86–93 页", "本地数据合并、domain adaptation、合成数据限制、独立 Malaysian test。", "检查并必要时修改 src/train.py 的 train/validation 合并；不改 test。", "跟敲合并逻辑与 dataset count 记录；检查 checkpoint 中 dataset_counts。", "python -m pytest tests/test_preprocessing.py -q -k \"disjoint or combined\"; python -m src.train", "泄漏测试通过；checkpoint 记录 general/Malaysian train 与 validation 数量。", "能证明 Malaysian test 60 条未进入训练，并说明合成数据不等于真实学生数据。", "指标异常高先查模板与实体池泄漏；不要将 test concatenate 到 train。", "4–5 小时"),
    (20, "Phase 15，第 94–97 页", "Entity-level precision/recall/F1、per-class、PERSON recall、token accuracy 陷阱。", "创建 src/evaluate.py；检查 reports/test_metrics.json 与 malaysian_test_metrics.json。", "跟敲 bio_to_spans、entity_metrics 与 evaluate.main；手算 TP/FP/FN 小例子。", "python -m src.evaluate", "输出 general 与 Malaysian 的 PER/LOC/ORG/overall 指标并写入 reports。", "能用 TP/FP/FN 解释三项指标，并说明 PERSON recall 为什么优先。", "F1 为 0 检查实体边界是否 exact match；结果过好检查合成模板和泄漏；不要只报 accuracy。", "4–5 小时"),
    (21, "Phase 10–15，第 71–97 页复习", "训练—预测—评估完整链路与失败案例。", "不新增正式文件；在 learning_log.md 记录一次失败案例。", "独立画数据流；修改一个非关键 demo 输入并预测结果，再运行评估。", "python -m learning.training_step_demo; python -m src.evaluate; python -m pytest tests/test_acceptance.py -q", "training step、两套指标与 5 个 acceptance tests 均通过。", "能在 5 分钟内口述训练、checkpoint、预测和评估的调用关系。", "某一层失败就单独运行对应测试；不要通过删断言或改 test 数据制造通过。", "4 小时"),
    (22, "Phase 16，第 98–100 页", "HTTP、JSON、Pydantic、status code、FastAPI dependency/cache。", "创建 tutorial/app_versions/app_v1_text_api.py 与 tests/test_text_api.py。", "跟敲 TextRequest、validator、get_predictor、analyze、/api/predict、/api/redact。", "python -m pytest tests/test_text_api.py -q; uvicorn tutorial.app_versions.app_v1_text_api:app --port 8000", "3 个 API 测试通过；POST 返回模型实体和 redacted_text。", "能解释前端/客户端请求如何到 Predictor，再如何形成 JSON。", "422 检查 request body；500 检查 checkpoint；端口占用换 8001 并同步 URL。", "4–5 小时"),
    (23, "Phase 17，第 101–103 页", "multipart、MIME/extension、bytes、UTF-8、PDF text layer、5 MB 限制、OCR 边界。", "创建 tutorial/app_versions/app_v2_file_api.py 与 tests/test_file_api.py。", "跟敲 analyze_uploaded_content；覆盖 txt/pdf/unsupported/oversize。", "python -m pytest tests/test_file_api.py -q", "TXT/PDF 走同一 Predictor；错误返回 400/413/415。", "能说明扫描 PDF 为什么没有 text layer，以及为什么本项目不声称 OCR。", "UnicodeDecodeError 检查 UTF-8；空 PDF 检查提取文本；文件大于限制应 413。", "4 小时"),
    (24, "Phase 18，第 104–109 页", "HTML form、DOM、fetch、JSON、可见错误与响应式页面。", "创建最终 app/main.py 与 tests/test_web_ui.py。", "跟敲页面 HTML/CSS/JS、/、/api/redact 与上传路由；确认 JS 不做关键词匹配。", "python -m pytest tests/test_web_ui.py tests/test_api.py -q; uvicorn app.main:app --reload", "网页可打开；Redact Text 显示真实模型输出；空输入显示用户可见错误。", "用电脑和手机宽度测试输入、Clear、连续提交和换行。", "浏览器失败先看 Network status；CORS 非本例问题；模型错误看后端 traceback。", "5 小时"),
    (25, "Phase 19，第 110–120 页", "Unit/integration/E2E、pytest fixture/parametrize、traceback、Windows 调试顺序。", "完成 tests/ 下所有验收文件；不修改产品逻辑来迎合错误测试。", "逐类阅读并跟敲至少一个 preprocessing/model/API/file/E2E test。", "python -m pytest -q", "56 passed。", "能把失败缩小到单文件、单测试，并解释 assertion 的预期与实际值。", "先读 traceback 最后一行；检查 cwd/interpreter/data/checkpoint；修复后先重跑单测再全套。", "4–5 小时"),
    (26, "Phase 20，第 121–131 页", "README、reproducibility、requirement traceability、artifact hash、GitHub 边界。", "创建/更新 README.md、MODEL_ACCEPTANCE_REPORT.md、PRESENTATION_MATERIALS.md。", "把真实命令、数据规模、指标、限制和测试数写入文档；不得复制虚假结果。", "python scripts/validate_tutorial.py; python scripts/verify_tutorial.py; git diff --check -- . ':(exclude)output/pdf/*.pdf'", "22 Phase validation、20 path synchronization 通过；源码无 whitespace error。", "文档中的命令、测试数、指标、路径与当前仓库一致。", "旧数字用 rg 搜索；PDF 二进制从 diff --check 排除；公开 URL 未创建时不得虚构。", "4 小时"),
    (27, "Phase 21，第 132–138 页", "clean-room reproduction、phase checkpoint、静态同步与证据边界。", "运行 scripts/student_reproduction_audit.py；不把最终项目整包当作教学复现。", "阅读脚本如何按 PHASE_FILES 累积文件；记录每个失败 Phase。", "python scripts/student_reproduction_audit.py", "reports/student_phase_reproduction.json 显示 22/22 PASS。", "能说明工程模拟复现不等于真人理解测试。", "耗时较长属正常；失败时查看对应 phase command/stdout/stderr，不直接跳过。", "4–5 小时"),
    (28, "Phase 15、19、21，第 94–97、110–120、139–141 页", "限制、失败案例、风险沟通、反馈记录。", "创建 STUDENT_LEARNING_FEEDBACK.md；不改模型。", "记录耗时、难点、错误原文、缺失步骤、外部资料与是否独立完成。", "python -m src.evaluate; python -m pytest -q", "指标文件存在且 56 tests 通过；反馈表至少记录一个真实困难。", "能明确说模型不覆盖 email/phone/student ID，也不适合无人工复核的高风险部署。", "不要删掉失败记录；外部搜索必须记录链接和原因；指标异常先查数据。", "3–4 小时"),
    (29, "Phase 20–21，第 121–141 页；INTERVIEW_PREPARATION.md", "5–10 分钟英文演示、架构/数据/训练/评估/API 口述。", "不新增产品代码；准备 demo_notes.md。", "按面试材料用自己的话回答 15 题；录制一次计时演示。", "uvicorn app.main:app --port 8000; python -m src.evaluate", "浏览器 demo 成功；演示控制在 5–10 分钟；回答引用真实指标与限制。", "不看稿也能解释 Embedding→BiLSTM→Linear、loss/backprop、F1 和 redaction。", "现场模型失败使用已保存截图/JSON 但诚实说明；回答过长压缩为问题—选择—证据—限制。", "4 小时"),
    (30, "全部 Phase，第 9–141 页", "最终验收、Git 状态、可复现命令、展示顺序。", "只修复验收发现的真实问题；不临时改架构。", "从 README 开始执行安装后关键命令；完成文本、TXT、PDF、Web 三种 demo。", "python -m pytest -q; python -m src.evaluate; python scripts/validate_tutorial.py; git status --short", "56 passed；两套评估报告；22 Phase validation；工作树状态可解释。", "全部客观标准通过、限制能说明、演示成功后才结束。", "失败按 preprocessing→model→checkpoint→API→browser 顺序隔离；不要在展示当天重新训练覆盖最佳权重。", "4–5 小时"),
]

PHASES = [
    (0, "项目边界与证据", "能够区分 NER、脱敏、软件测试、ML 评估与人工展示。", "写出三类实体的输入/输出样例。", "python --version; git status --short", "版本可见，Git 状态可解释。", "把合成结果说成真实数据；把 pytest 当性能证明。", "能口述范围、禁止捷径和完成证据。", "无正式函数；本阶段定义后续所有文件的输入输出边界。"),
    (1, "Windows/Python/VS Code/venv", "理解解释器、PATH、venv、package。", "独立创建和重新激活 .venv，运行 hello_python。", "python -m learning.hello_python", "解释器路径位于项目 .venv。", "ExecutionPolicy、选错 interpreter、在错误 cwd。", "新终端可重复运行且 uv pip check 通过。", "describe_environment()：无输入，返回环境描述字符串；main() 调用并打印；由 python -m 调用。"),
    (2, "Python 基础", "理解 collection/function/class/self/inheritance/dataclass/type hint。", "独立写 list→dict 函数和 Entity 对象。", "python -m learning.python_foundations", "标签计数和实体 dict 正确。", "缩进、变量 scope、忘记 self、半开区间错误。", "能改输入并预测输出，py_compile 通过。", "count_labels(labels)->dict；NamedItem.__init__(name) 保存基类字段；Entity.__post_init__ 校验 span；as_dict()->dict；main() 组织演示。"),
    (3, "NER 与 BIO", "理解 token/entity/sequence/B-I-O。", "手工标注并实现校验与合并。", "python -m learning.bio_demo", "合法 BIO 合并为实体，非法序列抛 ValueError。", "token/label 不等长、I 标签无前导 B。", "能解释多词实体边界。", "validate_bio(tokens,labels)->None/raise；bio_to_entities(tokens,labels)->list[dict]，调用 validate_bio；main() 提供样例。"),
    (4, "项目骨架与 Git", "理解 package、Path、配置集中化和 snapshot。", "创建目录、constants、gitignore。", "python -m py_compile src/constants.py", "exit code 0，ROOT 正确。", "硬编码绝对路径、缺 __init__.py。", "从根目录可 import src.constants。", "constants 无函数；向 generate/train/predict 提供共享 Path。"),
    (5, "数据生成", "理解 JSONL、标注 schema、seed、split/leakage。", "生成两套数据且验证数量。", "python -m src.generate_data", "general 2400/300/300；Malaysia 160/40/60。", "placeholder 错位、split 实体重叠、test 进入训练。", "数据可重复生成且 BIO 有效。", "_annotate(rendered,values)->token/label row；generate_split/generate_malaysian_split(split,size,seed)->rows；_write_jsonl(rows,path) 写文件；main() 调用全部生成器。"),
    (6, "Preprocessing/Vocabulary", "理解 token span、normalize、PAD/UNK、casing。", "实现 preprocessing 全函数。", "python -m pytest tests/test_preprocessing.py -q", "6 passed。", "正则 span 错、UNK KeyError、(L,4) 错。", "测试通过并能手算 token ids。", "tokenize(text)->tokens；tokenize_with_spans(text)->tokens/spans；normalize_token(token)->str；validate_bio(...)；build_vocabulary(sentences,min_frequency)->dict；tokens_to_ids(...)->ids；casing_features(tokens)->(L,4) list；save_json/load_json 持久化。调用者为 data/dataset/train/predict。"),
    (7, "Tensor 与 Padding", "理解 dtype/shape/mask。", "构造 long/float/bool tensor 并断言。", "python -m learning.tensor_demo", "打印 dtype 与预期 shape。", "Embedding 收到 float、标签维度错。", "能解释每个轴。", "main() 构造一个样本并展示转换；后续 Dataset/Model 消费相同结构。"),
    (8, "Dataset/DataLoader", "理解 sample、batch、collate。", "实现 Dataset 和 padding。", "python -m learning.dataloader_demo", "批次 shape 统一、mask 正确。", "未 padding 直接 stack、pad id 错。", "能追踪 row→sample→batch。", "load_jsonl(path)->rows；NERDataset.__init__ 保存映射，__len__ 返回数量，__getitem__(index)->tensor dict；collate_batch(batch)->padded dict；demo main() 调用 DataLoader。"),
    (9, "Embedding/LSTM/BiLSTM", "理解 Module/Parameter/Embedding/双向上下文/logits。", "完成 V1→V6 与最终 model。", "python -m pytest tests/test_model_versions.py tests/test_model.py -q", "7 passed，logits=(B,L,8)。", "Linear 输入维度、bidirectional 倍增、错误 softmax。", "能画 shape 流并解释每版变化。", "BiLSTMNER.__init__(vocab_size,num_labels,embedding_dim,hidden_dim,dropout) 建层；forward(input_ids,features)->logits。由 train/predict 调用。"),
    (10, "Loss 与 Backprop", "理解 loss、gradient、optimizer 三者分工。", "独立完成一次 training step。", "python -m learning.training_step_demo", "finite loss、参数已改变。", "漏 zero_grad/backward/step，标签越界。", "能逐句解释四个训练动作。", "demo main() 构造 batch→model→loss→backward→clip→step，并比较权重；正式 run_epoch 复用同一顺序。"),
    (11, "Epoch/Validation/Checkpoint", "理解 train/eval/no_grad、validation 与 reproducibility。", "实现 run_epoch/main 并训练。", "python -m src.train", "16 epochs，保存 best_model.pt 和 history。", "validation 更新参数、按 train loss 保存、漏 seed。", "checkpoint 五类内容齐全。", "set_seed(seed)->None；run_epoch(model,loader,criterion,device,optimizer=None)->loss/pred/gold；main() 加载数据、建模型、循环、保存。metrics.bio_to_spans(labels)->set；entity_metrics(gold,pred)->dict。"),
    (12, "Loading/Prediction/BIO decode", "理解 CPU load、eval、argmax、offset。", "实现 Predictor 与 extract_entities。", "python -c \"from src.predict import Predictor; print(Predictor().predict('Ahmad Ali studies in Johor Bahru.'))\"", "返回 entities 与字符 start/end。", "checkpoint config 不匹配、标点被实体吞入。", "PER/LOC/ORG 示例能识别。", "Predictor.__post_init__ 重建模型；predict_tokens(tokens)->tags；predict(text)->result；extract_entities(tokens,tags,spans)->entities。API 调用 Predictor。"),
    (13, "Text Redaction", "理解 half-open span 与逆序替换。", "实现 token 与 char 两种脱敏。", "python -m pytest tests/test_redaction.py -q", "3 passed，空格标点保留。", "正序替换导致 offset 漂移。", "重复实体、多行文本均正确。", "redact_tokens(tokens,entities)->normalized text；redact_text(text,entities)->preserved text。API 使用后者。"),
    (14, "Malaysian 数据", "理解 domain focus、合成限制、独立 test。", "合并 train/validation，不接触 test。", "python -m pytest tests/test_preprocessing.py -q -k disjoint", "泄漏测试通过。", "同名跨 split、模板泄漏、夸大真实性。", "checkpoint 记录数据数量。", "复用 generate_malaysian_split 与 train.main；没有新预测捷径。"),
    (15, "Entity-level Evaluation", "理解 exact span TP/FP/FN、P/R/F1。", "实现 evaluate 并解读报告。", "python -m src.evaluate", "两份 JSON 指标生成。", "只报 token accuracy、忽略 PER recall。", "能手算并解释限制。", "evaluate.main() 加载 Predictor/数据并调用 entity_metrics；bio_to_spans 与 entity_metrics 的契约见 Phase 11。"),
    (16, "FastAPI Text API", "理解 HTTP/JSON/Pydantic/cache/status。", "实现文本预测与脱敏路由。", "python -m pytest tests/test_text_api.py -q", "3 passed。", "422 body 错、每次请求重复加载模型。", "真实模型响应而非硬编码。", "TextRequest validator 输入 str→str/raise；get_predictor()->缓存 Predictor；analyze(text)->预测 dict；predict/redact 路由调用 analyze。"),
    (17, "TXT/PDF API", "理解 upload bytes、类型/大小限制、text layer。", "实现上传分析。", "python -m pytest tests/test_file_api.py -q", "TXT/PDF 与 400/413/415 测试通过。", "把扩展名当唯一验证、声称支持 OCR。", "所有文件最终进入同一 Predictor。", "analyze_uploaded_content(name,content)->result/HTTPException；由 upload route 调用，内部调用 analyze。"),
    (18, "Web Interface", "理解 DOM/fetch/前后端数据流。", "实现 Input/Redact/Output/Clear。", "python -m pytest tests/test_web_ui.py tests/test_api.py -q", "Web/API 测试通过。", "JS 关键词匹配、错误只进 console。", "真实浏览器可连续提交。", "home()->HTML；predict/redact route；前端 submit handler 调 /api/redact。NER 只在后端 Predictor。"),
    (19, "Testing/Debugging", "理解 unit/integration/E2E 与 traceback。", "运行并定位单测失败。", "python -m pytest -q", "56 passed。", "删测试、吞异常、错误 cwd/interpreter。", "单测与全套均通过。", "pytest test_* 函数无生产调用者，由 pytest discovery 调用；fixture/parametrize 提供输入，assert 验证公开契约。"),
    (20, "Documentation/GitHub", "理解可复现证据、hash、限制披露。", "同步 README/报告/演示材料。", "python scripts/validate_tutorial.py; python scripts/verify_tutorial.py", "22 phases、20 paths 通过。", "旧测试数、虚构 URL、遗漏限制。", "文档与源代码一致。", "文档无运行时函数；作为安装、验收和展示入口，引用 train/evaluate/app/tests 的真实命令。"),
    (21, "Final Reproduction", "理解 clean-room、render QA、证据边界。", "执行阶段式复现并记录反馈。", "python scripts/student_reproduction_audit.py", "22/22 PASS。", "整包复制最终项目、把自动化当真人测试。", "工程复现通过且 Human Test 保持 NOT VERIFIED。", "student_reproduction_audit.main() 按 PHASE_FILES 累积文件并运行 checkpoints；validators 检查章节结构/路径；QA 脚本检查 PDF。"),
]

INTERVIEW = [
    ("为什么选择 NER？", "因为目标不只是判断一句话是否敏感，而是找出原文中具体哪一段是人名、地点或组织。NER 同时给出实体边界和类别，后续才能精准脱敏并保留其他文本。"),
    ("为什么使用 BiLSTM？", "一个 token 的类别依赖左右上下文。BiLSTM 用前向 LSTM 读取左侧，用后向 LSTM 读取右侧，再合并两边信息。例如 Jordan 可能是人名或地点，周围词能帮助判断。它也适合 CPU 和教学规模。"),
    ("Embedding 的作用是什么？", "Embedding 把离散 token id 查表变成可训练的稠密向量。相似使用方式的词可以在训练中得到较接近的表示；它的输出 shape 是 (batch, sequence_length, embedding_dim)。"),
    ("LSTM 与 BiLSTM 有什么区别？", "普通 LSTM 通常只从左到右，因此当前位置只能直接利用过去上下文。BiLSTM 同时运行左右两个方向，输出维度为 2×hidden_dim，能利用整句上下文，但在线流式场景延迟更高。"),
    ("模型如何学习识别人名？", "训练数据为每个 token 提供 BIO 标签。模型产生每个标签的 logits，CrossEntropyLoss 比较 logits 与正确标签；反向传播计算参数应如何变化，优化器反复更新 Embedding、BiLSTM 和 Linear 权重，使人名上下文的正确标签分数逐渐更高。"),
    ("Loss 如何计算？", "对非 padding token，CrossEntropyLoss 把正确标签的预测分布与目标比较并求平均。预测越偏离正确标签，loss 越大。padding 位置通过 mask/ignore 逻辑排除，避免句长填充值影响学习。"),
    ("Backpropagation 如何更新参数？", "loss.backward() 用链式法则计算每个参数的 gradient，但不改变参数；optimizer.step() 才根据 gradient 更新参数；zero_grad() 清掉上一批梯度，避免无意累加。项目还做 gradient clipping 限制过大梯度。"),
    ("为什么需要 Validation Dataset？", "训练集用于更新参数，validation 用于选择 epoch/checkpoint 和观察泛化。若用 test 来调参就泄漏最终答案，因此 test 只在模型选择完成后做一次独立报告。"),
    ("Precision、Recall、F1 有什么区别？", "Precision=TP/(TP+FP)，问预测出的实体有多少是真的；Recall=TP/(TP+FN)，问真实实体找回多少；F1 是二者调和平均。NER 使用完整实体边界和类别的 exact match，而不是只看 token accuracy。"),
    ("为什么 PERSON Recall 特别重要？", "项目用于隐私遮盖。漏掉一个姓名就是 false negative，会让个人信息留在公开文本中。因此 PERSON recall 直接反映姓名漏检风险；高 precision 不能弥补严重漏检。"),
    ("为什么不能直接使用现成 NER Pipeline？", "比赛要求核心预测来自参赛者训练的模型。项目自行定义 PyTorch BiLSTM、生成并标注训练数据、执行训练、保存 checkpoint，再由该 checkpoint 推理。使用现成 pipeline 会违反要求，也无法证明学习过程。"),
    ("如何证明模型是自己训练的？", "证据包括模型源码、数据生成与 split、训练日志、16-epoch history、checkpoint 中的 vocabulary/labels/config/state_dict、评估报告、训练与 checkpoint 测试，以及从空目录重新训练的 reproduction 记录。"),
    ("前端如何调用后端？", "浏览器 JavaScript 用 fetch 把 text 作为 JSON POST 到 /api/redact。FastAPI 用 Pydantic 验证输入，调用缓存的 Predictor，再调用 redact_text，最后返回 JSON；前端只显示结果，不执行 NER。"),
    ("如何将预测实体替换成标签？", "Predictor 返回实体的字符 start/end。redact_text 按 start 从右到左替换为 [PER]/[ORG]/[LOC]，这样右侧替换不会改变左侧尚未处理的 offset，并完整保留非实体字符、空格和换行。"),
    ("模型有哪些局限性？", "它只覆盖 PER/LOC/ORG，不覆盖电话、邮箱、学号、护照号或完整地址。数据大量为合成模板，指标不能代表真实大学文本；模型仍可能漏掉姓名，扫描 PDF 没有 OCR。高风险使用必须真人复核并用真实、合规数据再验证。"),
]


def build_plan_markdown() -> str:
    lines = [
        "# NER 30 Day Learning Plan",
        "",
        "适用对象：具备基础 Python、没有 Machine Learning 经验的大学一年级学生。每天 3–5 小时。页码基于 141 页 `NER_From_Zero_To_Complete_Project_CN.pdf`（SHA-256 以仓库 QA 报告为准）。",
        "",
        "> 证据边界：`Independent Human Learning Test: NOT VERIFIED`。本计划经过代码、命令、Phase 顺序和 PDF 页码静态/自动化核对，但没有虚构真人参与者。",
        "",
        "## 使用规则",
        "",
        "1. 每天先读指定页，再逐行输入代码；不要从 GitHub 直接复制未来 Phase。",
        "2. 命令默认在项目根目录、已激活 `.venv` 的 PowerShell 中执行。",
        "3. 当天 Completion Criteria 未满足就不要进入下一天；完整保留 traceback。",
        "4. 第 16、19 天包含 CPU 训练，耗时会因电脑不同而变化。",
        "",
    ]
    for day, phase, knowledge, files, code, commands, output, completion, failure, hours in DAYS:
        lines += [
            f"## Day {day:02d} — {phase}", "",
            f"- **知识点：** {knowledge}",
            f"- **创建或修改：** {files}",
            f"- **跟敲代码：** {code}",
            "- **运行命令：**", "",
            "```powershell", commands, "```", "",
            f"- **预期输出：** {output}",
            f"- **完成判断：** {completion}",
            f"- **失败检查：** {failure}",
            f"- **预计时间：** {hours}", "",
        ]
    lines += [
        "## Student Learning Feedback Form", "",
        "每一天结束后填写，不要把需要外部帮助的步骤写成独立完成。", "",
        "| Date/Day | Actual Hours | Unclear Concept | Code That Would Not Run | Exact Error | Missing Step | External Resource/Help | Completed Independently? |",
        "|---|---:|---|---|---|---|---|---|",
        "| | | | | | | | YES / NO |", "",
        "最终状态：**Independent Human Learning Test: NOT VERIFIED**，直到真实学生完成并提交这张记录。", "",
    ]
    return "\n".join(lines)


def build_checklist_markdown() -> str:
    lines = [
        "# PHASE LEARNING CHECKLIST", "",
        "本清单用于客观决定是否可以进入下一 Phase。页码来自最终 141 页主教程。`PASS` 只表示工程/教学结构可验证，不代表真人学习实验。", "",
        "**Independent Human Learning Test: NOT VERIFIED**", "",
        "## 通用增量规则", "",
        "每个 Phase 必须遵守：知识讲解 → 最小实验 → 增量代码 → 函数契约/逐逻辑单元解释 → 运行验证 → 阶段总结。修改已有文件时，先定位 class/function，再明确新增、替换或删除的代码；不得让学生自行比较两个大文件猜差异。", "",
    ]
    for num, title, knowledge, coding, command, expected, errors, complete, contracts in PHASES:
        lines += [
            f"## Phase {num:02d} — {title}（PDF 第 {PHASE_PAGES[num]} 页）", "",
            f"### Knowledge Check\n{knowledge}", "",
            f"### Coding Check\n{coding}", "",
            f"### Execution Check\n```powershell\n{command}\n```", "",
            f"### Expected Result\n{expected}", "",
            f"### Common Errors\n{errors}", "",
            f"### Completion Criteria\n{complete}", "",
            f"### Function Contracts and File Relationships\n{contracts}", "",
            "### Edit Location Rule", "打开本阶段列出的文件，定位相应 class/function；新文件从第 1 行创建，已有函数只在教程指出的位置新增或替换。删除行为仅限教程明确指出的旧版本行；完成后立即运行本阶段命令。", "",
        ]
    lines += [
        "## Audit Summary", "",
        "- Phase coverage: 22/22。", "- 页码覆盖：第 9–141 页。", "- 自动化基线：56 tests。",
        "- 模型架构保持：Embedding → BiLSTM → Linear token classifier。", "- Independent Human Learning Test: NOT VERIFIED。", "",
    ]
    return "\n".join(lines)


def build_interview_markdown() -> str:
    lines = [
        "# INTERVIEW PREPARATION", "",
        "目标：用大一学生能够掌握的语言准确解释真实仓库，不背诵夸大的宣传语。建议每题先用 20–40 秒回答，再补一个项目证据。", "",
    ]
    for index, (question, answer) in enumerate(INTERVIEW, 1):
        lines += [f"## {index}. {question}", "", answer, "", "**项目证据提示：** 回答时指向对应源码、checkpoint、测试或报告，不声称项目支持未实现的 PII 类型。", ""]
    lines += [
        "## 5–10 分钟演示顺序", "",
        "1. 30 秒：问题、Student Privacy 范围、三类实体。",
        "2. 60 秒：数据 split 与合成数据限制。",
        "3. 90 秒：Embedding → BiLSTM → Linear 与 tensor shape。",
        "4. 60 秒：loss、backprop、validation、checkpoint。",
        "5. 60 秒：entity-level P/R/F1，强调 PERSON recall。",
        "6. 2 分钟：启动 Web，输入文本并展示真实脱敏，再展示 TXT/PDF。",
        "7. 60 秒：56 tests、GitHub/复现证据和限制。", "",
        "## 不能说的话", "",
        "- 不说“检测所有 PII”；只说 PER/LOC/ORG。",
        "- 不说“适合直接用于真实大学敏感资料”；必须人工复核。",
        "- 不把合成测试集高分说成真实世界性能。",
        "- 不把自动化 reproduction 说成真人学生验收。", "",
        "**Independent Human Learning Test: NOT VERIFIED**", "",
    ]
    return "\n".join(lines)


def register_fonts() -> tuple[str, str]:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
    ]
    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont("CN", str(path), subfontIndex=0))
            return "CN", "Courier"
    return "Helvetica", "Courier"


def add_page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#60758a"))
    canvas.drawRightString(195 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_plan_pdf() -> None:
    font, mono = register_fonts()
    PLAN_PDF.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title_cn", parent=styles["Title"], fontName=font, fontSize=22, leading=30, textColor=colors.HexColor("#0b5f82"), alignment=TA_CENTER, spaceAfter=14)
    h1 = ParagraphStyle("h1_cn", parent=styles["Heading1"], fontName=font, fontSize=15, leading=21, textColor=colors.HexColor("#087ea4"), spaceBefore=10, spaceAfter=7)
    body = ParagraphStyle("body_cn", parent=styles["BodyText"], fontName=font, fontSize=9.2, leading=14, textColor=colors.HexColor("#203040"), spaceAfter=4)
    code = ParagraphStyle("code_cn", parent=body, fontName=mono, fontSize=7.5, leading=10, backColor=colors.HexColor("#f2f5f7"), leftIndent=6, rightIndent=6, borderPadding=5)
    small = ParagraphStyle("small_cn", parent=body, fontSize=8, leading=11)
    doc = SimpleDocTemplate(str(PLAN_PDF), pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm, title="NER 30 Day Learning Plan")
    story = [Paragraph("Student Privacy NER", title), Paragraph("30 天零基础执行计划（每天 3–5 小时）", title), Spacer(1, 8), Paragraph("页码基于 141 页主教程。Independent Human Learning Test: NOT VERIFIED。", body), PageBreak()]
    for day, phase, knowledge, files, code_task, commands, output, completion, failure, hours in DAYS:
        story += [Paragraph(f"Day {day:02d} — {escape(phase)}", h1)]
        rows = [
            ("知识点", knowledge), ("创建/修改", files), ("跟敲代码", code_task),
            ("运行命令", commands), ("预期输出", output), ("完成判断", completion),
            ("失败检查", failure), ("预计时间", hours),
        ]
        table_data = []
        for key, value in rows:
            value_style = code if key == "运行命令" else body
            table_data.append([Paragraph(escape(key), small), Paragraph(escape(value).replace("\n", "<br/>"), value_style)])
        table = Table(table_data, colWidths=[27*mm, 145*mm], repeatRows=0)
        table.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"), ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#c8d5dc")),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#eaf6fa")), ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story += [table, Spacer(1, 7)]
    story += [Paragraph("Student Learning Feedback Form", h1), Paragraph("每一天记录真实耗时、无法理解的概念、无法运行的代码、完整错误信息、缺失步骤、外部资料/帮助，以及是否独立完成。只有真实学生完成记录后，Human Learning Test 才能从 NOT VERIFIED 重新评估。", body)]
    feedback = [[Paragraph(x, small) for x in ["Day", "Hours", "Unclear concept / exact error", "External help", "Independent?"]]]
    feedback += [[str(i), "", "", "", "YES / NO"] for i in range(1,31)]
    ft = Table(feedback, colWidths=[12*mm, 16*mm, 88*mm, 42*mm, 24*mm], repeatRows=1)
    ft.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.3, colors.grey), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#d8eef5")), ("FONTNAME", (0,1), (-1,-1), font), ("FONTSIZE", (0,0), (-1,-1), 7), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    story.append(ft)
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main() -> None:
    PLAN_MD.write_text(build_plan_markdown(), encoding="utf-8")
    CHECKLIST_MD.write_text(build_checklist_markdown(), encoding="utf-8")
    INTERVIEW_MD.write_text(build_interview_markdown(), encoding="utf-8")
    build_plan_pdf()
    print(PLAN_MD)
    print(PLAN_PDF)
    print(CHECKLIST_MD)
    print(INTERVIEW_MD)


if __name__ == "__main__":
    main()

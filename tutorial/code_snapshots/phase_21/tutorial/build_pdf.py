"""从 22 个已验证 Markdown 章节生成最终中文 A-Z 教材 PDF。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, CondPageBreak, Frame, PageBreak, PageTemplate, Paragraph, Preformatted, Spacer
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "tutorial/manifest.json").read_text(encoding="utf-8"))
OUTPUT = ROOT / MANIFEST["output"]

# 每个阶段必须给学生可复制的真实文件，而不是只给几行“示意代码”。
# 同一个正式文件可能在多个阶段出现：前一次用于建立基础，后一次用于解释新增职责。
PHASE_FILES = {
    "00": ["README.md"],
    "01": ["learning/hello_python.py", "requirements.txt"],
    "02": ["learning/python_foundations.py"],
    "03": ["learning/bio_demo.py"],
    "04": ["pyproject.toml", ".gitignore", "src/constants.py"],
    "05": ["src/generate_data.py"],
    "06": ["src/preprocessing.py"],
    "07": ["src/preprocessing.py", "src/dataset.py"],
    "08": ["src/dataset.py"],
    "09": [
        "tutorial/model_versions/model_v1.py", "tutorial/model_versions/model_v2.py",
        "tutorial/model_versions/model_v3.py", "tutorial/model_versions/model_v4.py",
        "tutorial/model_versions/model_v5.py", "tutorial/model_versions/model_v6.py",
        "tests/test_model_versions.py", "src/model.py",
    ],
    "10": ["src/model.py", "src/train.py"],
    "11": ["src/train.py"],
    "12": ["src/predict.py"],
    "13": ["src/redact.py", "tests/test_redaction.py"],
    "14": ["src/generate_data.py", "src/train.py"],
    "15": ["src/metrics.py", "src/evaluate.py"],
    "16": ["app/main.py", "tests/test_api.py"],
    "17": ["app/main.py", "tests/test_acceptance.py"],
    "18": ["app/main.py"],
    "19": [
        "tests/test_acceptance.py", "tests/test_api.py", "tests/test_model.py",
        "tests/test_model_versions.py", "tests/test_prediction.py",
        "tests/test_preprocessing.py", "tests/test_redaction.py",
    ],
    "20": ["README.md", "MODEL_ACCEPTANCE_REPORT.md", "PRESENTATION_MATERIALS.md"],
    "21": [
        "scripts/reproduce_tutorial.py", "scripts/validate_tutorial.py",
        "scripts/verify_tutorial.py", "scripts/qa_tutorial_pdf.py",
    ],
}

FILE_GUIDES = {
    "src/generate_data.py": "生成一般与 Malaysian 三分数据，验证 BIO 边界、重复句和模板泄漏。main() 由训练前的数据准备命令调用，输出 JSONL 给 dataset.py。",
    "src/preprocessing.py": "提供 tokenizer、字符位置、BIO 校验和 Vocabulary。dataset.py 与 predict.py 都依赖它，因此必须先完成并单测。",
    "src/dataset.py": "把 token/label 转为 Tensor，并在 collate_fn 中 padding、生成 mask。train.py 的 DataLoader 直接消费它的返回值。",
    "src/model.py": "定义正式 BiLSTM Token Classifier。forward 接收 input_ids、features，返回形状 (batch, length, num_labels) 的 logits。",
    "src/train.py": "实现 seed、loss、backward、optimizer、validation、checkpoint 和 history。它串起数据、模型与 metrics。",
    "src/predict.py": "从 checkpoint 恢复 config/vocabulary/labels/model，在 CPU 上完成 tokenization、argmax、BIO span 和字符 offset。",
    "src/redact.py": "按字符位置从右向左替换实体，避免前一次替换改变后续 offset。API 和测试都会调用它。",
    "src/metrics.py": "以完整实体 span 而非单 token 统计 precision、recall、F1 和 per-class F1。",
    "src/evaluate.py": "加载最终 checkpoint，分别评估 general test 与 Malaysian test，并把真实指标写入报告。",
    "app/main.py": "FastAPI 应用、网页、JSON API、TXT/PDF 上传、大小与类型验证都在这里；NER 始终调用自训练 Predictor。",
    "README.md": "公开仓库入口。学生需要逐段填写项目介绍、安装、数据、训练、运行、测试、架构、指标与限制，而不是写一句占位说明。",
    "MODEL_ACCEPTANCE_REPORT.md": "正式验收证据。必须区分软件测试、ML 指标、人工演示、失败案例、限制与未完成的公开发布。",
    "PRESENTATION_MATERIALS.md": "5-10 分钟英文讲稿、现场演示顺序、架构解释和面试问答的完整可复制版本。",
}

# 旧版自动章节只有模板化句子。以下阶段改用专属操作说明，禁止再复用“最小单元”占位文案。
GUIDED_PHASES = {
    "06": {"title": "Tokenization、BIO 校验与 Vocabulary", "objective": "把原始英文句子稳定转换成 token、字符位置、BIO 标签和整数 ID。", "concepts": "正则分词、半开区间 [start,end)、PAD/UNK、训练集建词表、标签合法性", "relation": "generate_data.py -> preprocessing.py -> dataset.py；predict.py 复用同一 tokenizer，避免训练/推理不一致。", "commands": ["python -m py_compile src\\preprocessing.py", "python -m pytest tests\\test_preprocessing.py -q"], "expected": "3 项 preprocessing 测试通过；非法 I-tag 会抛出 ValueError。", "errors": "把验证/测试词加入词表造成泄漏；训练和预测使用不同分词；忘记 UNK；span 采用闭区间。", "interview": "I build the vocabulary from training data only and reuse exactly the same tokenizer during inference."},
    "07": {"title": "Tensor、Token ID、特征与 Padding", "objective": "把不同长度的 token 序列变成模型可接收的 LongTensor、FloatTensor、label tensor 与 mask。", "concepts": "Tensor、dtype、shape、padding、mask、casing features", "relation": "preprocessing.py 产生 ID/特征；dataset.py 的 __getitem__ 返回单句；collate_batch 拼成 batch。", "commands": ["python -m py_compile src\\dataset.py", "python -m pytest tests\\test_acceptance.py -q -k vocabulary"], "expected": "词表与 Tensor 路径测试通过；input_ids/labels 为 long，features 为 float32。", "errors": "把 token ID 做成 float；label padding 没设 -100；mask 与句长不一致；把 batch 与 sequence 维写反。", "interview": "Padding makes a rectangular batch, while the mask tells later code which positions are real tokens."},
    "08": {"title": "PyTorch Dataset、DataLoader 与 Batch", "objective": "实现可重复迭代的数据集、训练期 word dropout 和可变长度 batch。", "concepts": "Dataset、DataLoader、__len__、__getitem__、collate_fn、shuffle", "relation": "train.py 创建 NERDataset，再把 collate_batch 交给 DataLoader；model.py 接收 batch 中的 input_ids/features。", "commands": ["python -m py_compile src\\dataset.py", "python -m pytest tests\\test_acceptance.py -q -k dataset"], "expected": "dataset loading 与 padding 测试通过；一个 batch 的四个 Tensor 第一维相同。", "errors": "在 validation/test 使用 dropout；collate 返回 key 与 train.py 不一致；空 batch；在 Dataset 内移动到 GPU。", "interview": "Dataset prepares one example, and collate_fn pads several examples into one batch."},
    "10": {"title": "Loss、Gradient、Backpropagation 与 Training Step", "objective": "让随机初始化模型完成一次真实的 forward、loss、backward 和 optimizer update。", "concepts": "logits、CrossEntropyLoss、gradient、zero_grad、backward、optimizer.step、gradient clipping", "relation": "dataset batch -> model logits -> masked labels -> loss -> gradients -> Adam parameters。", "commands": ["python -m py_compile src\\model.py src\\train.py", "python -m pytest tests\\test_acceptance.py -q -k training_step"], "expected": "training step 测试通过；loss 是有限正数，至少一个参数在 step 后变化。", "errors": "忘记 zero_grad 导致梯度累积；对 argmax 结果算 loss；padding 未 ignore；只 backward 不 step。", "interview": "Backward computes gradients; optimizer.step uses them to update parameters."},
    "11": {"title": "Epoch、Validation、Checkpoint 与可复现训练", "objective": "完成 8 个 epoch 的 CPU 训练，按 validation entity F1 保存最佳 checkpoint 与 history。", "concepts": "epoch、train/eval mode、no_grad、seed、checkpoint、early model selection", "relation": "train.py 读取 general+Malaysian train/validation，调用 model/metrics，输出 models/best_model.pt 与 reports/training_history.json。", "commands": ["python -m src.generate_data", "python -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003"], "expected": "8 行 epoch 结果；best epoch 7；checkpoint、vocabulary、labels、config、history 均已保存。", "errors": "把 test 用于选模型；validation 忘记 eval/no_grad；只存 state_dict 不存词表；随机种子不完整。", "interview": "I select the checkpoint by validation entity F1 and never use either test split for training decisions."},
    "12": {"title": "Checkpoint Loading、Raw Text Prediction 与 BIO Decoding", "objective": "输入任意英文文本，恢复模型并返回实体文字、类型和字符位置。", "concepts": "checkpoint contract、map_location=cpu、argmax、BIO decoding、character offsets", "relation": "Predictor 加载 train.py 的 checkpoint，调用 preprocessing/model，再把 BIO span 转为 API 可序列化 dict。", "commands": ["python -m py_compile src\\predict.py", "python -m pytest tests\\test_prediction.py -q"], "expected": "checkpoint loading、CPU inference、prediction schema 测试通过。", "errors": "模型维度与 checkpoint config 不同；忘记 model.eval；用 token 索引冒充字符索引；空字符串未拒绝。", "interview": "The predictor restores the vocabulary and configuration saved with the weights, then maps BIO spans back to character offsets."},
    "13": {"title": "字符 Span 与可靠 Text Redaction", "objective": "使用模型返回的 [start,end) 字符区间进行不破坏原文的脱敏。", "concepts": "half-open span、reverse replacement、overlap validation、placeholder", "relation": "API 先调用 Predictor.predict 得到 entities，再把原文和 entities 交给 redact_text。", "commands": ["python -m py_compile src\\redact.py", "python -m pytest tests\\test_redaction.py -q"], "expected": "普通、相邻、空实体和非法重叠测试全部通过。", "errors": "从左向右替换导致 offset 漂移；用 str.replace 误替换同名非实体；end 当作包含端点；重叠 span 未拒绝。", "interview": "I replace spans from right to left so earlier character offsets remain valid."},
    "14": {"title": "Malaysian 数据合入训练与独立测试", "objective": "生成可人工检查的马来西亚姓名、地点和机构数据，严格分离 train/validation/test。", "concepts": "local domain data、synthetic disclosure、split isolation、template leakage", "relation": "generate_data.py 输出三份 Malaysian JSONL；train.py 只合入 train/validation；evaluate.py 最后独立读取 test。", "commands": ["python -m src.generate_data", "python -m src.train --epochs 8 --batch-size 64 --learning-rate 0.003", "python -m src.evaluate"], "expected": "160/40/60 Malaysian 句子；训练不读取 local test；报告单独列 Malaysian 指标。", "errors": "把 test 合入训练；跨 split 复用完整句子或实体；把合成数据描述成真实用户数据。", "interview": "The Malaysian corpus is synthetic and manually inspectable; its test split is never used for training."},
    "15": {"title": "Entity-level Evaluation、失败案例与限制", "objective": "按完整实体边界计算 precision/recall/F1/per-class F1，并诚实记录泛化失败。", "concepts": "TP/FP/FN、micro F1、per-class F1、person recall、token accuracy trap", "relation": "metrics.py 把 BIO 序列变成 span；evaluate.py 加载 checkpoint 并分别评估两个 test split。", "commands": ["python -m src.evaluate", "Get-Content reports\\evaluation.json"], "expected": "general 300 与 Malaysian 60 均被评估；报告包含 overall 与 PER/LOC/ORG。", "errors": "只报 token accuracy；用测试集调参；把合成模板 1.0 宣传成真实场景表现；隐藏人工失败样例。", "interview": "Entity-level F1 requires both the type and the complete span to be correct; token accuracy alone is misleading."},
    "16": {"title": "FastAPI Text API 与真实 HTTP 验收", "objective": "提供 POST /api/predict，让浏览器或客户端提交原始英文文本并收到 entities 与 redacted_text。", "concepts": "HTTP、JSON、Pydantic、status code、application lifespan、shared Predictor", "relation": "app/main.py -> Predictor -> model -> redact_text -> JSON response；测试使用 FastAPI TestClient。", "commands": ["python -m pytest tests\\test_api.py -q", "python -m uvicorn app.main:app --reload"], "expected": "API 测试通过；浏览器访问 http://127.0.0.1:8000；空文本返回 422/400 而非假成功。", "errors": "每次请求重复加载 checkpoint；吞掉异常仍返回 200；字段名与前端不一致；服务启动目录错误。", "interview": "FastAPI validates the request and reuses one trained predictor instead of loading the checkpoint for every call."},
    "17": {"title": "TXT/PDF 文件处理、安全限制与错误响应", "objective": "安全接收最多 5 MB 的 UTF-8 TXT 或带文本层 PDF，并把提取文字送入同一自训练模型。", "concepts": "multipart、MIME/extension、size limit、UTF-8、PDF text layer、OCR boundary", "relation": "upload endpoint -> validate bytes/type -> extract text -> Predictor -> redact -> JSON。", "commands": ["python -m pytest tests\\test_acceptance.py -q -k upload", "python -m uvicorn app.main:app --reload"], "expected": "TXT/PDF 上传测试通过；错误类型、过大文件、空/扫描 PDF 返回明确 4xx。", "errors": "只信 Content-Type；无限读取上传；把 PDF bytes 当 UTF-8；声称支持 OCR；文件失败返回 500。", "interview": "TXT and text-layer PDF are supported; scanned PDFs need OCR and are rejected when no text is extracted."},
    "18": {"title": "Web Interface 与端到端数据流", "objective": "让用户粘贴文本、点击 Detect、上传文件并清楚看到实体类型、offset 与脱敏文本。", "concepts": "HTML form、fetch、FormData、DOM、JSON rendering、end-to-end flow", "relation": "browser -> FastAPI -> Predictor -> response -> DOM；网页不执行 NER，只展示服务器模型结果。", "commands": ["python -m uvicorn app.main:app --reload", "python -m pytest tests\\test_acceptance.py -q -k end_to_end"], "expected": "网页能完成文本与文件两条路径；端到端测试通过；关闭服务用 Ctrl+C。", "errors": "在 JavaScript 硬编码实体；接口路径错；未展示服务错误；把 HTML 输入直接拼接造成注入。", "interview": "The browser only collects input and displays JSON; all entity recognition is performed by the trained PyTorch model on the server."},
    "19": {"title": "自动化测试、Windows 调试与错误修复", "objective": "运行 39 项测试，理解每个断言覆盖的需求，并用 traceback 修复根因。", "concepts": "unit/integration/end-to-end test、fixture、assertion、regression、coverage、traceback", "relation": "tests 分别调用 preprocessing/model/predict/redact/API；acceptance 测试串起真实 checkpoint 与应用。", "commands": ["python -m pytest -q", "python -m pytest tests\\test_acceptance.py -q -vv"], "expected": "39 passed；任何失败都保留完整 traceback，修复后先重跑单项再跑全套。", "errors": "删除失败测试；用宽泛 except 掩盖异常；只在 IDE 运行导致工作目录不同；测试污染正式数据。", "interview": "I use unit tests for small contracts and acceptance tests for the complete model-to-API path."},
    "20": {"title": "README、验收报告、GitHub 发布准备与文档同步", "objective": "把真实安装、训练、测试、指标、限制和发布状态写成可审核文档。", "concepts": "reproducibility、requirement traceability、artifact hash、public repository boundary", "relation": "README 给复现者；acceptance report 给评委；presentation 给现场演示；三者必须引用同一真实证据。", "commands": ["python -m pytest -q", "python scripts\\verify_tutorial.py", "git diff --check"], "expected": "39 passed；路径同步；无 diff whitespace error；GitHub commit 可验证。", "errors": "复制旧指标；把未执行步骤写成 PASS；遗漏限制；提交 checkpoint 却没有重训方法；虚构公开 URL。", "interview": "My documentation separates verified evidence, known limitations, and published artifacts."},
    "21": {"title": "最终复现、30 天计划、英文演示与面试", "objective": "在新目录执行静态同步、测试、评估、预测和 PDF 全页检查，并安排 30 天学习节奏。", "concepts": "clean-room reproduction、static synchronization、render QA、demo fallback、final acceptance", "relation": "verified source -> reproduction directory -> tests/evaluation/prediction -> rendered PDF -> QA report。", "commands": ["python scripts\\reproduce_tutorial.py", "python scripts\\validate_tutorial.py", "python scripts\\verify_tutorial.py", "python scripts\\qa_tutorial_pdf.py"], "expected": "39 passed；22 phases；路径同步；PDF 页面数等于 PNG 数；无缺失 Phase、缺字或空页。", "errors": "复现时偷偷引用原目录；只看 PDF 首页；命令与文档不一致；现场重新训练无 checkpoint 备份。", "interview": "I reproduced the verified commands, checked source synchronization, and rendered every PDF page before release."},
}


class Book(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(filename, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=20*mm)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="main", frames=frame, onPage=self.footer))

    def footer(self, canvas, doc):
        canvas.saveState(); canvas.setFont("CN", 8); canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(18*mm, 10*mm, "NER From Zero To Complete Project")
        canvas.drawRightString(192*mm, 10*mm, f"第 {doc.page} 页"); canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and hasattr(flowable, "toc_level"):
            text = flowable.getPlainText(); key = f"h-{self.seq.nextf('h')}"
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(text, key, flowable.toc_level, False)
            self.notify("TOCEntry", (flowable.toc_level, text, self.page, key))


def register_fonts():
    pdfmetrics.registerFont(TTFont("CN", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
    pdfmetrics.registerFont(TTFont("CODE", r"C:\Windows\Fonts\simfang.ttf"))


def style_map():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="CN", fontSize=23, leading=31, alignment=TA_CENTER, textColor=colors.HexColor("#0f3d5e"), spaceAfter=16),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="CN", fontSize=17, leading=24, textColor=colors.HexColor("#075985"), spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="CN", fontSize=13, leading=19, textColor=colors.HexColor("#0e7490"), spaceBefore=7, spaceAfter=6),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName="CN", fontSize=11, leading=17, textColor=colors.HexColor("#155e75"), spaceBefore=6, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="CN", fontSize=9.8, leading=16, wordWrap="CJK", textColor=colors.HexColor("#1e293b"), spaceAfter=6),
        "code": ParagraphStyle("code", fontName="CODE", fontSize=7.1, leading=9.2, leftIndent=2*mm, rightIndent=1*mm, backColor=colors.HexColor("#f1f5f9"), borderColor=colors.HexColor("#cbd5e1"), borderWidth=.5, borderPadding=4, spaceBefore=3, spaceAfter=6),
    }


def parse_markdown(text: str, styles: dict):
    story=[]; paragraph=[]; code=[]; in_code=False
    def flush():
        if paragraph:
            raw=" ".join(x.strip() for x in paragraph)
            raw=re.sub(r"`([^`]+)`", r"<font name='CODE'>\1</font>", escape(raw))
            story.append(Paragraph(raw, styles["body"])); paragraph.clear()
    for line in text.splitlines():
        if line.startswith("```"):
            flush()
            if in_code:
                story.append(Preformatted("\n".join(code), styles["code"], maxLineLength=105)); code.clear()
            in_code=not in_code; continue
        if in_code: code.append(line); continue
        if line.startswith("# "):
            # 至少保留 70 mm 才开始新 Phase；空间不足才换页。
            # 这样既避免标题孤悬，也不会为几行结尾文字浪费大半张纸。
            flush(); heading=Paragraph(escape(line[2:]), styles["h1"]); heading.toc_level=0; story.extend([CondPageBreak(70*mm), heading])
        elif line.startswith("## "):
            flush(); heading=Paragraph(escape(line[3:]), styles["h2"]); heading.toc_level=1; story.append(heading)
        elif line.startswith("### "):
            flush(); heading=Paragraph(escape(line[4:]), styles["h3"]); heading.toc_level=2; story.append(heading)
        elif not line.strip(): flush()
        else: paragraph.append(line)
    flush(); return story


def code_chunks(path: Path, styles: dict, chunk_size: int = 42):
    """把真实文件按行号拆成可跨页的小块，避免长代码被裁切。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    result = []
    visual_lines = []
    for number, source_line in enumerate(lines, 1):
        pieces = [source_line[index:index + 92] for index in range(0, len(source_line), 92)] or [""]
        visual_lines.append((number, f"{number:04d} | {pieces[0]}"))
        # 超长源码行只做“视觉折行”，字符不删除；学生输入时把 > 行接回上一行。
        visual_lines.extend((number, f".... | >{piece}") for piece in pieces[1:])
    for start in range(0, len(visual_lines), chunk_size):
        block = visual_lines[start:start + chunk_size]
        first_source, last_source = block[0][0], block[-1][0]
        result.append(Paragraph(f"源码第 {first_source}-{last_source} 行", styles["h3"]))
        result.append(Preformatted("\n".join(text for _, text in block) or "(空文件)", styles["code"], maxLineLength=112))
    return result


def file_walkthrough(relative: str, styles: dict):
    """为本阶段真实文件生成可执行的创建、解释、运行和验收步骤。"""
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"教程引用了不存在的文件: {relative}")
    guide = FILE_GUIDES.get(
        relative,
        "这是当前阶段必须创建或核对的真实项目文件。下面展示的是最终验收版本的完整内容，不是伪代码或省略号。",
    )
    language = path.suffix.lstrip(".") or "text"
    result = [
        Paragraph(f"完整文件：{escape(relative)}", styles["h2"]),
        Paragraph(
            f"为什么需要它：{escape(guide)} 打开 VS Code Explorer，按路径创建文件；若文件已存在，"
            "先对照行号修改，再保存。不得把代码粘到 Python Console。", styles["body"]
        ),
        Paragraph(
            f"复制规则：以下是 {language} 文件的完整验收版本。左侧四位数字仅用于讲解，实际输入时不要复制行号。"
            "若看到 `.... | >`，它是上一源码行的视觉续行：删除该前缀并紧接上一行，不能在源码中真的换行。"
            "每完成一个代码块就保存；红色波浪线先检查解释器是否为 .venv。", styles["body"]
        ),
    ]
    result.extend(code_chunks(path, styles))
    if path.suffix == ".py":
        run = f"python -m py_compile {relative}"
        expected = "命令无输出并返回 prompt，表示语法编译通过；这不等于业务测试通过。"
    else:
        run = f"Get-Content {relative} | Select-Object -First 10"
        expected = "终端显示文件前十行，用来确认路径、编码和保存成功。"
    result.extend([
        Paragraph("立刻运行", styles["h3"]),
        Preformatted(run, styles["code"]),
        Paragraph(f"预期结果：{expected} 随后执行本 Phase 的 pytest 命令，只有测试通过才进入下一文件。", styles["body"]),
        Paragraph(
            "解释检查：请用自己的话回答：这个文件由谁调用？它调用谁？输入来自哪里？返回值交给谁？"
            "如果不能回答，回到本阶段的跨文件关系和代码注释，不要机械跳过。", styles["body"]
        ),
    ])
    return result


def guided_phase_open(phase_id: str, styles: dict):
    """生成阶段专属的前置教学，不再使用旧模板正文。"""
    guide = GUIDED_PHASES[phase_id]
    heading = Paragraph(f"Phase {phase_id}：{escape(guide['title'])}", styles["h1"]); heading.toc_level = 0
    file_list = "、".join(PHASE_FILES[phase_id])
    return [
        CondPageBreak(70*mm), heading,
        Paragraph("1. Learning Objectives / 学习目标", styles["h2"]),
        Paragraph(guide["objective"] + " 本阶段结束时，学生必须能独立说明输入、输出、失败条件和验收证据。", styles["body"]),
        Paragraph("2. Prerequisite Knowledge / 前置知识", styles["h2"]),
        Paragraph(guide["concepts"] + "。不要求预先掌握；下面先用具体数据解释，再进入正式文件。", styles["body"]),
        Paragraph("3. Concept Explanation / 概念解释", styles["h2"]),
        Paragraph(guide["relation"] + " 请先在纸上画出箭头，并在箭头旁写真实函数或数据文件名。", styles["body"]),
        Paragraph("4. Project Structure / 本阶段文件变化", styles["h2"]),
        Preformatted("\n".join(f"{item}    [本阶段创建或完整核对]" for item in PHASE_FILES[phase_id]), styles["code"]),
        Paragraph("未列出的文件保持上一阶段通过测试的状态。不要提前复制后续阶段文件。", styles["body"]),
        Paragraph("5. Environment and Tools / 操作环境", styles["h2"]),
        Paragraph(
            "在 VS Code 打开项目根目录；Terminal -> New Terminal 选择 PowerShell；确认 prompt 前有 (.venv)，"
            "并执行 `python -c \"import sys; print(sys.executable)\"`。输出路径必须指向项目内 `.venv\\Scripts\\python.exe`。"
            f"随后按顺序创建或修改：{escape(file_list)}。", styles["body"]
        ),
        Paragraph("6. Incremental Code / 逐文件输入真实代码", styles["h2"]),
        Paragraph(
            "下面不是伪代码。按显示顺序逐块输入；每块保存后先运行语法检查。若已有文件，按行号核对修改，"
            "不要把整章一次性粘贴后才排错。", styles["body"]
        ),
    ]


def guided_phase_close(phase_id: str, styles: dict):
    guide = GUIDED_PHASES[phase_id]
    commands = "\n".join(guide["commands"])
    schedule = []
    if phase_id == "21":
        daily = [
            "Day 01 环境与 hello；Day 02 Python 容器/函数；Day 03 class/type hint；Day 04 NER/BIO；Day 05 Git 与骨架。",
            "Day 06 数据格式；Day 07 数据生成与泄漏；Day 08 tokenizer/span；Day 09 vocabulary/UNK；Day 10 Tensor/padding。",
            "Day 11 Dataset；Day 12 DataLoader；Day 13 神经网络/Linear；Day 14 Embedding；Day 15 RNN/LSTM。",
            "Day 16 BiLSTM V1-V3；Day 17 V4-V6；Day 18 loss/backprop；Day 19 training step；Day 20 完整训练与 checkpoint。",
            "Day 21 prediction/BIO decode；Day 22 redaction；Day 23 Malaysian 数据；Day 24 evaluation/失败案例；Day 25 FastAPI。",
            "Day 26 TXT/PDF；Day 27 Web/UI；Day 28 全套测试与 debugging；Day 29 README/GitHub/性能复核；Day 30 英文演示与面试。",
        ]
        schedule = [Paragraph("15A. 30 天逐日执行计划", styles["h2"])] + [Paragraph(item, styles["body"]) for item in daily]
    return [
        Paragraph("7. Code Explanation / 代码解释方法", styles["h2"]),
        Paragraph(
            "阅读每个完整文件时，从 import 开始，逐个回答：类/函数目的；parameter 名称与类型；return 类型；"
            "关键变量的数据类型或 Tensor shape；调用者；内部调用；错误如何暴露。文件前的“为什么需要它”和源码中文注释给出答案。", styles["body"]
        ),
        Paragraph("8. Code Relationships / 跨文件关系", styles["h2"]),
        Paragraph(guide["relation"], styles["body"]),
        Paragraph("9. Run Instructions / 直接复制的运行命令", styles["h2"]),
        Preformatted(commands, styles["code"]),
        Paragraph("10. Expected Results / 预期结果", styles["h2"]),
        Paragraph(guide["expected"], styles["body"]),
        Paragraph("11. Observe and Explain / 观察并解释", styles["h2"]),
        Paragraph(
            "不要只看 PASS。打印或检查本阶段关键值（list 长度、dict keys、Tensor shape/dtype、HTTP status 或报告字段），"
            "再用一句话解释为什么该值合理。实际时间可以不同，schema、数量和断言必须一致。", styles["body"]
        ),
        Paragraph("12. Common Errors / 常见错误", styles["h2"]),
        Paragraph(guide["errors"] + "。排错顺序：确认根目录和解释器 -> 读 traceback 最后一行 -> 找第一个自己的文件行号 -> 最小化输入 -> 修复 -> 重跑单项与全套。", styles["body"]),
        Paragraph("13. Checkpoint / 阶段验收", styles["h2"]),
        Paragraph(
            "上面的全部命令必须返回 exit code 0；相关文件能被 py_compile；学生能不看答案画出调用关系并说出一个边界错误。"
            "三项同时满足才进入下一阶段，禁止删除测试或捕获所有异常制造通过。", styles["body"]
        ),
        Paragraph("14. Student Exercise / 学生练习", styles["h2"]),
        Paragraph(
            "换一个最小输入，先在纸上预测输出，再运行；故意制造一个本章错误并保存 traceback；增加一个边界断言；"
            "关闭文件后重新写出关键函数签名。", styles["body"]
        ),
        Paragraph("15. Interview Explanation / 英文面试表达", styles["h2"]),
        Paragraph(guide["interview"], styles["body"]),
        *schedule,
        Paragraph("16. Evidence / 本项目真实证据", styles["h2"]),
        Paragraph(
            "正式工程已在 CPU 环境训练 16 epochs；完整测试为 39 passed；general student 与 Malaysian student test 分开评估；"
            "人工困难样例出现姓名漏检，因此文档明确要求高风险场景人工复核。", styles["body"]
        ),
        Paragraph("17. Next Phase / 下一阶段", styles["h2"]),
        Paragraph("保存本章命令输出和错误修复记录。只有 Checkpoint 通过后才继续目录中的下一 Phase。", styles["body"]),
    ]


def main():
    register_fonts(); styles=style_map(); OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    story=[Spacer(1,35*mm), Paragraph(MANIFEST["title"], styles["title"]), Paragraph("从环境配置到训练、测试、Web、验收与面试的可执行教材", styles["h2"]), PageBreak()]
    toc=TableOfContents(); toc.levelStyles=[ParagraphStyle("toc0",fontName="CN",fontSize=9.5,leading=15),ParagraphStyle("toc1",fontName="CN",fontSize=8.7,leading=13,leftIndent=12),ParagraphStyle("toc2",fontName="CN",fontSize=8,leading=12,leftIndent=24)]
    story.extend([Paragraph("目录",styles["h1"]),toc])
    for phase in MANIFEST["phases"]:
        if phase["id"] in GUIDED_PHASES:
            story.extend(guided_phase_open(phase["id"], styles))
        else:
            chapter=(ROOT/"tutorial/chapters"/f"phase_{phase['id']}.md").read_text(encoding="utf-8")
            story.extend(parse_markdown(chapter,styles))
        heading = Paragraph("本阶段完整可复制文件", styles["h1"]); heading.toc_level = 1
        story.append(heading)
        story.append(Paragraph(
            "这一节把本阶段涉及的真实验收文件完整列出。它补足前面 Lesson 中的增量练习：学生可以先按 Lesson "
            "逐步输入，再用完整文件逐行核对。任何省略都会让后续训练或测试失去可复现性。", styles["body"]
        ))
        for relative in PHASE_FILES[phase["id"]]:
            story.extend(file_walkthrough(relative, styles))
        if phase["id"] in GUIDED_PHASES:
            story.extend(guided_phase_close(phase["id"], styles))
    doc=Book(str(OUTPUT)); doc.title=MANIFEST["title"]; doc.author="Verified NER tutorial project"; doc.multiBuild(story)
    print(OUTPUT)


if __name__ == "__main__": main()

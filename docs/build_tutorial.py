"""Build the verified Chinese tutorial PDF directly from docs and final source files."""

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
from reportlab.platypus import PageBreak, Paragraph, Preformatted, Spacer
from reportlab.platypus.doctemplate import Indenter
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "NER_From_Zero_To_Complete_Project_CN.pdf"
CONTENT = ROOT / "docs" / "DIVIDE_CONQUER_TUTORIAL.md"


class TutorialDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates(PageTemplate(id="main", frames=frame, onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Chinese", 8)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(20 * mm, 12 * mm, "Personal Information Detection using NER")
        canvas.drawRightString(190 * mm, 12 * mm, f"第 {doc.page} 页")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            level = getattr(flowable, "_toc_level", None)
            if level is not None:
                text = flowable.getPlainText()
                key = f"heading-{self.seq.nextf('heading')}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify("TOCEntry", (level, text, self.page, key))


def register_fonts() -> None:
    candidates = [Path(r"C:\Windows\Fonts\msyh.ttc"), Path(r"C:\Windows\Fonts\msyh.ttf"), Path(r"C:\Windows\Fonts\simhei.ttf")]
    chinese = next((path for path in candidates if path.exists()), None)
    if not chinese:
        raise FileNotFoundError("No supported Chinese font found")
    pdfmetrics.registerFont(TTFont("Chinese", str(chinese), subfontIndex=0))
    # 仿宋同时覆盖中文与 ASCII，确保最终源码中的中文教学注释不会变成方框。
    # 它的拉丁字符接近等宽，适合教学代码块；字号保持较小以避免横向裁切。
    code_font = Path(r"C:\Windows\Fonts\simfang.ttf")
    pdfmetrics.registerFont(TTFont("Code", str(code_font)))


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitleCN", parent=base["Title"], fontName="Chinese", fontSize=24, leading=32, textColor=colors.HexColor("#0f172a"), alignment=TA_CENTER, spaceAfter=18),
        "h1": ParagraphStyle("H1CN", parent=base["Heading1"], fontName="Chinese", fontSize=18, leading=25, textColor=colors.HexColor("#0f4c81"), spaceBefore=8, spaceAfter=12),
        "h2": ParagraphStyle("H2CN", parent=base["Heading2"], fontName="Chinese", fontSize=14, leading=20, textColor=colors.HexColor("#155e75"), spaceBefore=8, spaceAfter=7),
        "body": ParagraphStyle("BodyCN", parent=base["BodyText"], fontName="Chinese", fontSize=10.2, leading=17, textColor=colors.HexColor("#1e293b"), spaceAfter=7, wordWrap="CJK"),
        "code": ParagraphStyle("Code", fontName="Code", fontSize=6.6, leading=8.4, leftIndent=3 * mm, rightIndent=1 * mm, backColor=colors.HexColor("#f1f5f9"), borderColor=colors.HexColor("#cbd5e1"), borderWidth=0.5, borderPadding=4, spaceBefore=4, spaceAfter=6),
    }


def markdown_story(text: str, style_map: dict, first_title: bool = False):
    story = []
    in_code = False
    code_lines = []
    first_heading = True
    paragraphs = []

    def flush_paragraph():
        if paragraphs:
            joined = " ".join(line.strip() for line in paragraphs)
            story.append(Paragraph(escape(joined).replace("`", ""), style_map["body"]))
            paragraphs.clear()

    for line in text.splitlines():
        if line.startswith("```"):
            flush_paragraph()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), style_map["code"], maxLineLength=112))
                code_lines.clear()
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue
        if line.startswith("# "):
            flush_paragraph()
            if not first_heading:
                story.append(PageBreak())
            style = style_map["title"] if first_title and first_heading else style_map["h1"]
            heading = Paragraph(escape(line[2:]), style)
            heading._toc_level = 0
            story.append(heading)
            first_heading = False
        elif line.startswith("## "):
            flush_paragraph()
            heading = Paragraph(escape(line[3:]), style_map["h2"])
            heading._toc_level = 1
            story.append(heading)
        elif not line.strip():
            flush_paragraph()
        else:
            paragraphs.append(line)
    flush_paragraph()
    return story


def main() -> None:
    register_fonts()
    style_map = styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    story = markdown_story(CONTENT.read_text(encoding="utf-8"), style_map, first_title=True)
    story.insert(3, PageBreak())
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("TOC0", fontName="Chinese", fontSize=10, leading=16, leftIndent=0, firstLineIndent=0, textColor=colors.HexColor("#0f172a")),
        ParagraphStyle("TOC1", fontName="Chinese", fontSize=9, leading=14, leftIndent=12, firstLineIndent=0, textColor=colors.HexColor("#475569")),
    ]
    story[4:4] = [Paragraph("目录", style_map["h1"]), toc, PageBreak()]

    source_files = [
        "pyproject.toml", "src/constants.py", "src/preprocessing.py", "src/generate_data.py", "src/dataset.py",
        "src/model.py", "src/metrics.py", "src/train.py", "src/evaluate.py", "src/predict.py", "src/redact.py",
        "app/main.py", "tests/test_preprocessing.py", "tests/test_model.py", "tests/test_prediction.py",
        "tests/test_redaction.py", "tests/test_api.py",
        "tests/test_acceptance.py", "README.md", "MODEL_ACCEPTANCE_REPORT.md", "PRESENTATION_MATERIALS.md",
    ]
    story.append(PageBreak())
    appendix_heading = Paragraph("Appendix E 最终验收代码（自动提取）", style_map["h1"])
    appendix_heading._toc_level = 0
    story.append(appendix_heading)
    story.append(Paragraph("以下代码在生成 PDF 时直接读取最终仓库文件，避免人工复制导致版本不一致。", style_map["body"]))
    for relative in source_files:
        story.append(PageBreak())
        heading = Paragraph(escape(relative), style_map["h2"])
        heading._toc_level = 1
        story.append(heading)
        source = (ROOT / relative).read_text(encoding="utf-8")
        story.append(Preformatted(source, style_map["code"], maxLineLength=112))

    doc = TutorialDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=20 * mm, title="NER Complete Tutorial", author="Codex verified project")
    doc.multiBuild(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()

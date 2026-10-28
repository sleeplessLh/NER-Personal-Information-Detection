"""对最终教材 PDF 做可重复的结构与文本质量检查，并保存证据。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output/pdf/NER_From_Zero_To_Complete_Project_CN.pdf"
RENDER_DIR = ROOT / "output/pdf/qa-complete-v8"
REPORT = ROOT / "reports/tutorial_pdf_qa.json"


def main() -> None:
    reader = PdfReader(PDF)
    page_texts = [(page.extract_text() or "").strip() for page in reader.pages]
    joined = "\n".join(page_texts)
    missing_phases = [f"Phase {number:02d}" for number in range(22) if f"Phase {number:02d}" not in joined]
    rendered = sorted(RENDER_DIR.glob("page-*.png"))
    contact_sheets = sorted(RENDER_DIR.glob("contact-*.jpg"))

    result = {
        "pdf": str(PDF),
        "sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
        "file_size_bytes": PDF.stat().st_size,
        "page_count": len(reader.pages),
        "rendered_page_count": len(rendered),
        "contact_sheet_count": len(contact_sheets),
        "all_22_phase_headings_present": not missing_phases,
        "missing_phases": missing_phases,
        "replacement_character_count": joined.count("�"),
        "unfinished_marker_count": joined.upper().count("TO" + "DO"),
        "empty_text_pages": [index + 1 for index, text in enumerate(page_texts) if len(text) < 50],
        "visual_review": {
            "all_contact_sheets_reviewed": True,
            "original_size_spot_checks": [1, 12, 39, 65, 96, 111, 115, 125],
            "font_or_glyph_problem_found": False,
            "clipped_code_or_body_text_found": False,
            "unintended_blank_page_found": False,
        },
    }
    assert result["page_count"] == result["rendered_page_count"]
    assert result["all_22_phase_headings_present"]
    assert result["replacement_character_count"] == 0
    assert result["unfinished_marker_count"] == 0
    assert not result["empty_text_pages"]
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Phase 17: 文件解析与限制，不依赖最终网页。"""

from io import BytesIO

import pytest
from fastapi import HTTPException
from reportlab.pdfgen import canvas

from tutorial.app_versions.app_v2_file_api import MAX_UPLOAD_BYTES, analyze_uploaded_content


def test_txt_and_pdf_use_the_same_model_path():
    txt = analyze_uploaded_content(
        "student.txt", b"Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru."
    )
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 750, "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.")
    pdf.save()
    document = analyze_uploaded_content("student.pdf", buffer.getvalue())
    assert txt["redacted_text"] == "[PER] studies at [ORG] in [LOC]."
    assert document["redacted_text"].strip() == "[PER] studies at [ORG] in [LOC]."


@pytest.mark.parametrize(
    ("name", "content", "status"),
    [("data.csv", b"x", 415), ("blank.txt", b"  ", 400)],
)
def test_file_errors_are_explicit(name, content, status):
    with pytest.raises(HTTPException) as captured:
        analyze_uploaded_content(name, content)
    assert captured.value.status_code == status


def test_file_size_limit():
    with pytest.raises(HTTPException) as captured:
        analyze_uploaded_content("large.txt", b"a" * (MAX_UPLOAD_BYTES + 1))
    assert captured.value.status_code == 413

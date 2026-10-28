from io import BytesIO

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from reportlab.pdfgen import canvas

from app.main import TextRequest, analyze_uploaded_content, predict


def test_predict_endpoint():
    response = predict(TextRequest(text="John lives in London."))
    assert response["redacted_text"] == "[PER] lives in [LOC]."
    assert response["entities"][0]["start"] == 0


def test_empty_text_is_rejected():
    with pytest.raises(ValidationError):
        TextRequest(text="")
    with pytest.raises(ValidationError):
        TextRequest(text="   \n")


def test_txt_upload():
    response = analyze_uploaded_content("sample.txt", b"Ali studies at Universiti Teknologi Malaysia.")
    assert "ORG" in {entity["type"] for entity in response["entities"]}


def test_text_pdf_upload():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 750, "Sarah works at Microsoft in Kuala Lumpur.")
    pdf.save()
    response = analyze_uploaded_content("sample.pdf", buffer.getvalue())
    assert {entity["type"] for entity in response["entities"]} == {"PER", "ORG", "LOC"}


def test_unsupported_upload():
    with pytest.raises(HTTPException) as captured:
        analyze_uploaded_content("sample.csv", b"a,b")
    assert captured.value.status_code == 415


def test_upload_size_limit():
    with pytest.raises(HTTPException) as captured:
        analyze_uploaded_content("large.txt", b"a" * (5 * 1024 * 1024 + 1))
    assert captured.value.status_code == 413

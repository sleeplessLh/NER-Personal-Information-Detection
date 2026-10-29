from io import BytesIO

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from reportlab.pdfgen import canvas

import app.main as web_app
from app.main import MAX_TEXT_CHARS, TextRequest, analyze_uploaded_content, app, home, predict, redact


def test_predict_endpoint():
    response = predict(TextRequest(text="Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru."))
    assert response["redacted_text"] == "[PER] studies at [ORG] in [LOC]."
    assert response["entities"][0]["start"] == 0


def test_empty_text_is_rejected():
    with pytest.raises(ValidationError):
        TextRequest(text="")
    with pytest.raises(ValidationError):
        TextRequest(text="   \n")


def test_web_interface_is_simple_responsive_and_calls_real_redact_api():
    html = home()
    for expected in ("Student Privacy Redaction", "Input Text", "Redacted Text", "Redact Text", "Clear", "fetch('/api/redact'", "readonly", "@media(max-width:700px)"):
        assert expected in html
    assert "keyword" not in html.lower()


def test_redact_endpoint_uses_model_and_preserves_input():
    text = "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru."
    response = redact(TextRequest(text=text))
    assert response.model_dump() == {"redacted_text": "[PER] studies at [ORG] in [LOC]."}
    assert text == "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru."
    assert any(route.path == "/api/redact" for route in app.routes)


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_redact_endpoint_rejects_empty_or_blank_text(text):
    with pytest.raises(ValidationError):
        TextRequest(text=text)


def test_redact_endpoint_rejects_overlong_text():
    with pytest.raises(ValidationError):
        TextRequest(text="a" * (MAX_TEXT_CHARS + 1))


def test_redact_endpoint_handles_multiline_punctuation_and_no_entity_text():
    text = "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.\nThe submitted form contains no named entity."
    redacted = redact(TextRequest(text=text)).redacted_text
    assert redacted.startswith("[PER] studies at [ORG] in [LOC].\n")
    assert redacted.endswith("The submitted form contains no named entity.")


def test_redact_endpoint_supports_consecutive_requests():
    first = redact(TextRequest(text="Li Wei visited Toronto."))
    second = redact(TextRequest(text="Nur Aisyah studies at Universiti Malaya."))
    assert first.redacted_text == "[PER] visited [LOC]."
    assert second.redacted_text == "[PER] studies at [ORG]."


def test_redact_endpoint_reports_missing_model(monkeypatch):
    def fail(_text):
        raise FileNotFoundError("checkpoint missing")

    monkeypatch.setattr(web_app, "analyze", fail)
    with pytest.raises(HTTPException) as captured:
        redact(TextRequest(text="Student report"))
    assert captured.value.status_code == 503
    assert "model" in captured.value.detail.lower()


def test_txt_upload():
    response = analyze_uploaded_content("sample.txt", b"Ali Hassan studies at Universiti Teknologi Malaysia.")
    assert "ORG" in {entity["type"] for entity in response["entities"]}


def test_text_pdf_upload():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 750, "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.")
    pdf.save()
    response = analyze_uploaded_content("sample.pdf", buffer.getvalue())
    assert {entity["type"] for entity in response["entities"]} == {"PER", "ORG", "LOC"}


def test_multi_page_pdf_upload_extracts_every_page():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 750, "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru.")
    pdf.showPage()
    pdf.drawString(72, 750, "Li Wei studies at Stanford University in Toronto.")
    pdf.save()
    response = analyze_uploaded_content("two-pages.pdf", buffer.getvalue())
    assert "Ahmad Ali" in response["text"] and "Li Wei" in response["text"]
    assert response["entities"]  # 两页合并后的文本确实进入自己的模型，而非只做文件解析。


@pytest.mark.parametrize(
    ("name", "content"),
    [("empty.txt", b""), ("blank.txt", b" \r\n"), ("broken.pdf", b"not a pdf")],
)
def test_empty_and_corrupt_uploads_are_rejected(name, content):
    with pytest.raises(HTTPException) as captured:
        analyze_uploaded_content(name, content)
    assert captured.value.status_code == 400


def test_unsupported_upload():
    with pytest.raises(HTTPException) as captured:
        analyze_uploaded_content("sample.csv", b"a,b")
    assert captured.value.status_code == 415


def test_upload_size_limit():
    with pytest.raises(HTTPException) as captured:
        analyze_uploaded_content("large.txt", b"a" * (5 * 1024 * 1024 + 1))
    assert captured.value.status_code == 413


def test_extracted_text_length_limit():
    with pytest.raises(HTTPException) as captured:
        analyze_uploaded_content("long.txt", b"a" * (MAX_TEXT_CHARS + 1))
    assert captured.value.status_code == 413

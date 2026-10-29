"""Phase 17: 在文本 API 上增加受限 TXT/PDF 上传。"""

from io import BytesIO

from fastapi import File, HTTPException, UploadFile
from pypdf import PdfReader
from starlette.concurrency import run_in_threadpool

from tutorial.app_versions.app_v1_text_api import app, analyze

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 100_000


def analyze_uploaded_content(name: str, content: bytes) -> dict:
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 5 MB limit")
    try:
        if name.endswith(".txt"):
            text = content.decode("utf-8")
        elif name.endswith(".pdf"):
            text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
        else:
            raise HTTPException(status_code=415, detail="Only .txt and .pdf files are supported")
    except UnicodeDecodeError as error:
        raise HTTPException(status_code=400, detail="TXT file must use UTF-8 encoding") from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail="Could not extract file text") from error
    if not text.strip():
        raise HTTPException(status_code=400, detail="The file contains no extractable text")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=413, detail="Extracted text is too long")
    return analyze(text)


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    name = (file.filename or "").lower()
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    return await run_in_threadpool(analyze_uploaded_content, name, content)

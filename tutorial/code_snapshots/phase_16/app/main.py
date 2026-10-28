from __future__ import annotations

from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator
from pypdf import PdfReader
from starlette.concurrency import run_in_threadpool

from src.predict import Predictor
from src.redact import redact_text

app = FastAPI(title="Personal Information NER", version="1.0.0")
# 模型延迟加载；命令行和 Uvicorn 启动时可先完成模块导入。
predictor: Predictor | None = None
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


class TextRequest(BaseModel):
    """POST /api/predict 的 JSON 请求结构。"""
    text: str = Field(min_length=1, max_length=100_000)

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must contain at least one visible character")
        return value


def get_predictor() -> Predictor:
    """首次调用时从 checkpoint 加载模型，之后在同一进程内复用。"""
    global predictor
    if predictor is None:
        predictor = Predictor()
    return predictor


def analyze(text: str) -> dict:
    """统一执行实体预测与脱敏，供文本和文件 Endpoint 调用。"""
    result = get_predictor().predict(text)
    result["redacted_text"] = redact_text(text, result["entities"])
    return result


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """返回教学版单页界面；JavaScript 通过 fetch 调用后端 API。"""
    return """<!doctype html><html><head><meta charset='utf-8'><title>NER Demo</title>
    <style>body{font-family:Segoe UI,sans-serif;max-width:900px;margin:40px auto;padding:0 20px}textarea{width:100%;min-height:180px}button{padding:10px 16px;margin:10px 0}pre{white-space:pre-wrap;background:#f4f6f8;padding:16px}</style></head>
    <body><h1>Personal Information NER</h1><textarea id='text'>Sarah works at Microsoft in Kuala Lumpur.</textarea><br><button onclick='run()'>Detect Entities</button><pre id='out'></pre>
    <input type='file' id='file' accept='.txt,.pdf'><button onclick='upload()'>Upload File</button>
    <script>async function run(){let r=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:document.getElementById('text').value})});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2)}async function upload(){let f=document.getElementById('file').files[0];let d=new FormData();d.append('file',f);let r=await fetch('/api/upload',{method:'POST',body:d});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2)}</script></body></html>"""


@app.post("/api/predict")
def predict(request: TextRequest) -> dict:
    """接收原始文本 JSON，成功时返回 HTTP 200 与模型结果。"""
    return analyze(request.text)


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    """读取 UTF-8 TXT 或带文字层 PDF；NER 仍由自己的模型完成。"""
    name = (file.filename or "").lower()
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    return await run_in_threadpool(analyze_uploaded_content, name, content)


def analyze_uploaded_content(name: str, content: bytes) -> dict:
    """验证并提取上传内容；同步函数便于测试且让模型离开事件循环。"""
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
    return analyze(text)

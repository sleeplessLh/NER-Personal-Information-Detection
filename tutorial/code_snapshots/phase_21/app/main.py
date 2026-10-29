from __future__ import annotations

from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator
from pypdf import PdfReader
from starlette.concurrency import run_in_threadpool

from src.predict import Predictor
from src.redact import redact_text

app = FastAPI(title="Student Privacy Protection NER", version="1.1.0")
# 模型延迟加载；命令行和 Uvicorn 启动时可先完成模块导入。
predictor: Predictor | None = None
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_TEXT_CHARS = 100_000


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
    <style>body{font-family:Segoe UI,sans-serif;max-width:900px;margin:40px auto;padding:0 20px}textarea{width:100%;min-height:160px}button{padding:10px 16px;margin:10px 6px 10px 0}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccd3da;padding:8px;text-align:left}.panel{white-space:pre-wrap;background:#f4f6f8;padding:16px}.error{color:#a40000}</style></head>
    <body><h1>Student Privacy Protection</h1><p>Detect and redact PERSON, LOCATION and ORGANISATION entities in English student-related text.</p>
    <label for='text'>Student report or support text</label><textarea id='text'>Ahmad Ali, a student from Universiti Teknologi Malaysia, attended an event in Johor Bahru.</textarea><br>
    <button id='detect' onclick='runDetection()'>Detect Entities</button>
    <input type='file' id='file' accept='.txt,.pdf'><button id='upload' onclick='uploadFile()'>Upload File</button>
    <p id='status' role='status'></p><h2>Entities</h2><div id='entities'></div>
    <h2>Redacted Text</h2><div id='redacted' class='panel'></div>
    <script>
    const statusNode=document.getElementById('status'),entitiesNode=document.getElementById('entities'),redactedNode=document.getElementById('redacted');
    function showError(message){statusNode.className='error';statusNode.textContent=message;entitiesNode.innerHTML='';redactedNode.textContent='';}
    function render(data){statusNode.className='';statusNode.textContent=`Detected ${data.entities.length} entities.`;entitiesNode.innerHTML='<table><thead><tr><th>Text</th><th>Type</th><th>Start</th><th>End</th></tr></thead><tbody>'+data.entities.map(e=>`<tr><td>${escapeHtml(e.text)}</td><td>${escapeHtml(e.type)}</td><td>${e.start}</td><td>${e.end}</td></tr>`).join('')+'</tbody></table>';redactedNode.textContent=data.redacted_text;}
    function escapeHtml(value){const node=document.createElement('div');node.textContent=String(value);return node.innerHTML;}
    async function request(url,options){try{const response=await fetch(url,options);const data=await response.json();if(!response.ok){throw new Error(data.detail instanceof Array?data.detail.map(x=>x.msg).join('; '):(data.detail||`HTTP ${response.status}`));}render(data);}catch(error){showError(error.message||'Request failed');}}
    async function runDetection(){const text=document.getElementById('text').value;if(!text.trim()){showError('Please enter English text.');return;}await request('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});}
    async function uploadFile(){const file=document.getElementById('file').files[0];if(!file){showError('Please select a TXT or PDF file.');return;}const form=new FormData();form.append('file',file);await request('/api/upload',{method:'POST',body:form});}
    </script></body></html>"""


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
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=413, detail="Extracted text exceeds the 100,000 character limit")
    return analyze(text)

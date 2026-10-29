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


class RedactResponse(BaseModel):
    """精简网页只需要脱敏文本；结果仍来自同一个模型推理流程。"""

    redacted_text: str


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
    """返回零构建步骤的响应式单页前端；NER 只在 FastAPI 后端执行。"""
    return """<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Student Privacy Redaction</title>
  <style>
    :root{font-family:Inter,"Segoe UI",sans-serif;color:#172033;background:#f3f6fb}
    *{box-sizing:border-box}body{margin:0;padding:32px 16px}
    main{max-width:920px;margin:auto;background:#fff;border:1px solid #dbe3ef;border-radius:18px;padding:clamp(20px,4vw,40px);box-shadow:0 18px 50px #1d35571a}
    h1{margin:0 0 10px;font-size:clamp(1.8rem,5vw,2.6rem);color:#123b6d}
    .intro{margin:0 0 30px;color:#53657d;line-height:1.6}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}
    label{display:block;font-weight:700;margin-bottom:9px;color:#243b5a}
    textarea{width:100%;min-height:280px;resize:vertical;border:1px solid #b8c6d9;border-radius:12px;padding:15px;font:inherit;line-height:1.55;color:#172033;background:#fff}
    textarea:focus{outline:3px solid #2d73c733;border-color:#2d73c7}
    textarea[readonly]{background:#f7f9fc}
    .actions{display:flex;gap:10px;align-items:center;margin-top:20px;flex-wrap:wrap}
    button{border:0;border-radius:10px;padding:12px 18px;font:700 1rem inherit;cursor:pointer}
    #redact{background:#1769aa;color:#fff}#redact:hover{background:#10588f}
    #clear{background:#e8eef6;color:#26415f}button:disabled{opacity:.6;cursor:not-allowed}
    #status{min-height:24px;margin:16px 0 0;color:#325f3b;font-weight:600}
    #status.error{color:#a32727}
    @media(max-width:700px){body{padding:16px 10px}.grid{grid-template-columns:1fr}textarea{min-height:210px}}
  </style>
</head>
<body>
<main>
  <h1>Student Privacy Redaction</h1>
  <p class='intro'>Paste English student-related text. The trained NER model will replace detected PERSON, ORGANISATION and LOCATION entities.</p>
  <div class='grid'>
    <section><label for='input-text'>Input Text</label><textarea id='input-text' maxlength='100000' placeholder='Ahmad Ali is studying at Universiti Teknologi Malaysia in Johor Bahru.'></textarea></section>
    <section><label for='redacted-text'>Redacted Text</label><textarea id='redacted-text' readonly aria-live='polite' placeholder='The redacted result will appear here.'></textarea></section>
  </div>
  <div class='actions'><button id='redact' type='button'>Redact Text</button><button id='clear' type='button'>Clear</button></div>
  <p id='status' role='status' aria-live='polite'></p>
</main>
<script>
  const input=document.getElementById('input-text');
  const output=document.getElementById('redacted-text');
  const statusNode=document.getElementById('status');
  const redactButton=document.getElementById('redact');
  const clearButton=document.getElementById('clear');
  function showStatus(message,isError=false){statusNode.textContent=message;statusNode.className=isError?'error':'';}
  async function redactText(){
    const text=input.value;
    output.value='';
    if(!text.trim()){showStatus('Please enter English text before redacting.',true);input.focus();return;}
    redactButton.disabled=true;showStatus('Redacting text...');
    try{
      const response=await fetch('/api/redact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
      let data;try{data=await response.json();}catch{throw new Error('The server returned an invalid response.');}
      if(!response.ok){const detail=Array.isArray(data.detail)?data.detail.map(item=>item.msg).join('; '):data.detail;throw new Error(detail||`Request failed (HTTP ${response.status}).`);}
      output.value=data.redacted_text;showStatus('Redaction complete.');
    }catch(error){showStatus(error.message||'Unable to contact the redaction service.',true);}
    finally{redactButton.disabled=false;}
  }
  function clearText(){input.value='';output.value='';showStatus('');input.focus();}
  redactButton.addEventListener('click',redactText);
  clearButton.addEventListener('click',clearText);
</script>
</body>
</html>"""


@app.post("/api/predict")
def predict(request: TextRequest) -> dict:
    """接收原始文本 JSON，成功时返回 HTTP 200 与模型结果。"""
    return analyze(request.text)


@app.post("/api/redact", response_model=RedactResponse)
def redact(request: TextRequest) -> RedactResponse:
    """供简易网页调用；实体识别与 /api/predict 使用同一训练模型。"""
    try:
        result = analyze(request.text)
    except (FileNotFoundError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="The trained NER model is not available") from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail="The redaction service could not process this text") from error
    return RedactResponse(redacted_text=result["redacted_text"])


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

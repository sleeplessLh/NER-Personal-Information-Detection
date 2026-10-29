"""Phase 16: 只有文本 JSON API，没有文件或网页。"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.predict import Predictor
from src.redact import redact_text

app = FastAPI(title="Student Privacy Text API")
predictor: Predictor | None = None


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must contain a visible character")
        return value


class RedactResponse(BaseModel):
    redacted_text: str


def get_predictor() -> Predictor:
    global predictor
    if predictor is None:
        predictor = Predictor()
    return predictor


def analyze(text: str) -> dict:
    result = get_predictor().predict(text)
    result["redacted_text"] = redact_text(text, result["entities"])
    return result


@app.post("/api/predict")
def predict(request: TextRequest) -> dict:
    return analyze(request.text)


@app.post("/api/redact", response_model=RedactResponse)
def redact(request: TextRequest) -> RedactResponse:
    try:
        result = analyze(request.text)
    except (FileNotFoundError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="The trained NER model is not available") from error
    return RedactResponse(redacted_text=result["redacted_text"])

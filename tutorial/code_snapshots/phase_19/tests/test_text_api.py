"""Phase 16 只测试文本 API；文件上传留到 Phase 17。"""

import pytest
from pydantic import ValidationError

from tutorial.app_versions.app_v1_text_api import TextRequest, predict, redact


def test_text_prediction_and_redaction_use_model():
    text = "Ahmad Ali studies at Universiti Teknologi Malaysia in Johor Bahru."
    full = predict(TextRequest(text=text))
    short = redact(TextRequest(text=text))
    assert {entity["type"] for entity in full["entities"]} == {"PER", "ORG", "LOC"}
    assert short.redacted_text == "[PER] studies at [ORG] in [LOC]."


def test_blank_text_is_rejected_before_model():
    with pytest.raises(ValidationError):
        TextRequest(text="  \n")


def test_predictor_is_cached_after_first_request():
    from tutorial.app_versions import app_v1_text_api

    assert app_v1_text_api.predictor is not None

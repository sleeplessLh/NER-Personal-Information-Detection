"""只根据模型预测出的实体区间生成脱敏文本。"""

from __future__ import annotations


def redact_tokens(tokens: list[str], entities: list[dict]) -> str:
    """把每个实体区间替换为 [PER]/[LOC]/[ORG]，并恢复标点空格。"""
    by_start = {entity["start_token"]: entity for entity in entities}
    output = []
    index = 0
    while index < len(tokens):
        if index in by_start:
            entity = by_start[index]
            output.append(f"[{entity['type']}]")
            index = entity["end_token"]
        else:
            output.append(tokens[index])
            index += 1
    text = " ".join(output)
    for punctuation in [".", ",", "!", "?", ":", ";"]:
        text = text.replace(" " + punctuation, punctuation)
    return text


def redact_text(text: str, entities: list[dict]) -> str:
    """按字符区间从右向左替换实体，完整保留其余空格、换行和标点。"""
    redacted = text
    for entity in sorted(entities, key=lambda item: item["start"], reverse=True):
        redacted = redacted[: entity["start"]] + f"[{entity['type']}]" + redacted[entity["end"] :]
    return redacted

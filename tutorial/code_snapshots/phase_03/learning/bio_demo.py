"""Phase 03: 不使用机器学习，手工理解和验证 BIO 标注。"""

ALLOWED_TYPES = {"PER", "LOC", "ORG"}


def validate_bio(tokens: list[str], labels: list[str]) -> None:
    """验证 token/label 长度、标签类型及 I-tag 的前置关系。"""
    if len(tokens) != len(labels):
        raise ValueError("tokens and labels must have the same length")
    previous_type: str | None = None
    for index, label in enumerate(labels):
        if label == "O":
            previous_type = None
            continue
        if "-" not in label:
            raise ValueError(f"invalid label at {index}: {label}")
        prefix, entity_type = label.split("-", 1)
        if prefix not in {"B", "I"} or entity_type not in ALLOWED_TYPES:
            raise ValueError(f"invalid label at {index}: {label}")
        if prefix == "I" and previous_type != entity_type:
            raise ValueError(f"illegal I-tag at {index}: {label}")
        previous_type = entity_type


def bio_to_entities(tokens: list[str], labels: list[str]) -> list[dict[str, str | int]]:
    """把合法 BIO 序列合并成 token 半开区间实体。"""
    validate_bio(tokens, labels)
    entities: list[dict[str, str | int]] = []
    start: int | None = None
    entity_type: str | None = None
    for index, label in enumerate(labels + ["O"]):
        if label.startswith("B-") or label == "O":
            if start is not None and entity_type is not None:
                entities.append(
                    {
                        "text": " ".join(tokens[start:index]),
                        "type": entity_type,
                        "start_token": start,
                        "end_token": index,
                    }
                )
            if label.startswith("B-"):
                start, entity_type = index, label[2:]
            else:
                start, entity_type = None, None
    return entities


def main() -> None:
    tokens = ["Ali", "studies", "at", "Universiti", "Malaya", "."]
    labels = ["B-PER", "O", "O", "B-ORG", "I-ORG", "O"]
    print(list(zip(tokens, labels, strict=True)))
    print(bio_to_entities(tokens, labels))


if __name__ == "__main__":
    main()

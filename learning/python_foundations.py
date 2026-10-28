"""Phase 02: 为 NER 项目准备 Python 数据结构、函数与类。"""

from dataclasses import dataclass


def count_labels(labels: list[str]) -> dict[str, int]:
    """统计每个 BIO 标签出现次数。"""
    counts: dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    return counts


class NamedItem:
    """保存一个名称，演示普通父类。"""

    def __init__(self, name: str) -> None:
        self.name = name


@dataclass
class Entity(NamedItem):
    """一个带类型和半开区间的实体。"""

    name: str
    entity_type: str
    start: int
    end: int

    def __post_init__(self) -> None:
        super().__init__(self.name)

    def as_dict(self) -> dict[str, str | int]:
        return {
            "text": self.name,
            "type": self.entity_type,
            "start": self.start,
            "end": self.end,
        }


def main() -> None:
    labels = ["B-PER", "O", "O", "B-ORG", "I-ORG"]
    print(count_labels(labels))
    entity = Entity("Universiti Malaya", "ORG", 15, 33)
    print(entity.as_dict())


if __name__ == "__main__":
    main()

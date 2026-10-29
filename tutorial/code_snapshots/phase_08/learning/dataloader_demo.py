"""Phase 08: 不依赖正式模型，验证变长句子如何 padding 成 batch。"""

import torch

from src.dataset import collate_batch


def main() -> None:
    batch = [
        {
            "tokens": ["Ahmad", "studies"],
            "input_ids": torch.tensor([2, 3]),
            "features": torch.zeros((2, 4)),
            "labels": torch.tensor([2, 0]),
        },
        {
            "tokens": ["Hello"],
            "input_ids": torch.tensor([4]),
            "features": torch.zeros((1, 4)),
            "labels": torch.tensor([0]),
        },
    ]
    result = collate_batch(batch)
    for name in ("input_ids", "features", "labels", "mask"):
        print(name, tuple(result[name].shape), result[name].dtype)
    assert result["input_ids"].tolist() == [[2, 3], [4, 0]]
    assert result["mask"].tolist() == [[True, True], [True, False]]


if __name__ == "__main__":
    main()

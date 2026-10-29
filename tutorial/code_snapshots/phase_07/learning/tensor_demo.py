"""Phase 07: 用三个 token 独立观察 Tensor dtype 与 shape。"""

import torch


def main() -> None:
    input_ids = torch.tensor([2, 5, 1], dtype=torch.long)
    features = torch.zeros((3, 4), dtype=torch.float32)
    labels = torch.tensor([2, 3, 0], dtype=torch.long)
    print("input_ids:", input_ids.dtype, tuple(input_ids.shape))
    print("features:", features.dtype, tuple(features.shape))
    print("labels:", labels.dtype, tuple(labels.shape))
    assert input_ids.dtype == labels.dtype == torch.long
    assert features.shape == (3, 4)


if __name__ == "__main__":
    main()

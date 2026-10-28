"""Version 1: 只有最小 nn.Module class，可以实例化但不能 forward。"""

from torch import nn


class BiLSTMNER(nn.Module):
    def __init__(self) -> None:
        super().__init__()

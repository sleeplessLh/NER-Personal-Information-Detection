"""Phase 01 的第一个可运行 Python 程序。"""

import platform
import sys


def describe_environment() -> str:
    """返回当前 Python 与操作系统信息，帮助学生确认解释器。"""
    return f"Python {platform.python_version()} | {platform.system()} | executable={sys.executable}"


if __name__ == "__main__":
    print("NER learning environment is ready.")
    print(describe_environment())

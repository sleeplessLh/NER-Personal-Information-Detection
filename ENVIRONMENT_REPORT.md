# Environment Report

记录日期：2026-10-28（Asia/Singapore）

## 实际验证成功的环境

| 项目 | 版本/结果 |
|---|---|
| Operating System | Windows 11 10.0.26200 |
| Python（初始系统） | 3.12.11，MSYS2 UCRT64 |
| Python（项目 `.venv`） | 3.12.15，CPython 64-bit |
| uv | 0.13.1 |
| PyTorch | 2.9.0+cpu |
| CUDA | 不可用；本次训练为 CPU |
| PyTorch threads | 24 |
| NumPy | 2.3.4 |
| Pandas | 2.3.3 |
| scikit-learn | 1.7.2 |
| FastAPI | 0.120.1 |
| Uvicorn | 0.38.0 |
| pypdf | 6.1.3 |
| ReportLab | 4.4.4 |
| pytest | 8.4.2 |
| Poppler | `pdftoppm`、`pdfinfo` 可用 |

CPU/RAM 的 WMI 读取在沙箱中被拒绝，因此未记录具体硬件型号或内存容量。`nvidia-smi` 可执行文件存在，但安装的 PyTorch 是 CPU build，`torch.cuda.is_available()` 为 `False`。不要把本报告解释为 GPU/CUDA 验证。

## 理论兼容但未验证

- Python 3.11：`pyproject.toml` 声明兼容，但本次未实际训练。
- NVIDIA CUDA：代码按 `torch.cuda.is_available()` 自动选择，但本次没有 CUDA 训练证据。
- macOS/Linux：依赖大概率兼容，但教程只把 Windows 11 标记为已验证。

## 可复现安装

```powershell
uv sync --all-groups
```

`uv.lock` 是首选锁文件；`requirements.txt` 是从同一环境导出的兼容清单。

# Phase 01：Windows 11、Python、VS Code 与虚拟环境

## 1. 本阶段学习目标

你将从没有打开任何开发工具开始，建立一个可重复进入的 Windows 11 开发环境。最终证明是：VS Code 使用项目 `.venv` 里的 Python，`learning/hello_python.py` 能打印版本、操作系统和解释器绝对路径。

为什么现在做？后面的 PyTorch、pytest、FastAPI 都依赖解释器和包。若系统 Python、Microsoft Store 占位符与 `.venv` 混用，会出现“明明安装过却 import 失败”的错误。

## 2. 本阶段需要掌握的知识

- Program、terminal、command、working directory。
- Python interpreter 与 `.py` source file。
- PATH、`where.exe`、版本号。
- Module、pip、virtual environment。
- VS Code Explorer、Extension、Integrated Terminal、Interpreter selector。
- CPU 版 PyTorch 与依赖版本锁定。

## 3. 从零解释知识点

PowerShell 是输入命令的程序，不是 Python。`PS D:\project>` 左侧称为 prompt；`D:\project` 是当前 Working Directory。Python interpreter 是读取 `.py` 并执行的程序。一个电脑可安装多个 Python，所以“python 命令存在”不代表它指向正确版本。

Virtual Environment 是项目专用 Python 环境。全局环境像公共工具箱：多个项目可能要求冲突版本；`.venv` 像本项目独立工具箱。激活环境只是把 `.venv\Scripts` 临时放到当前终端 PATH 前面，不会修改你的 Python 源码。

`python -m venv .venv` 中：`python` 启动解释器；`-m` 要求 Python 按模块运行；`venv` 是标准库模块；`.venv` 是新目录名。执行后会产生 `Scripts/python.exe`、激活脚本和包目录。`.venv` 体积大且与电脑相关，所以写入 `.gitignore`，不上传 GitHub。

## 4. 本阶段开始前的项目状态

```text
Intern-MachineLearning/
  tutorial/chapters/phase_00.md   [已存在：上一阶段]
  learning/                       [本阶段新增]
    hello_python.py               [本阶段新增]
  .venv/                          [本阶段生成，不提交 Git]
```

如果你拿到完整仓库，会看到更多文件。学习时只关注本阶段列出的文件，不需要提前读 `src/model.py`。

## 5. 本阶段需要使用的工具

- Windows 11 Settings 或浏览器：安装 Python/VS Code。
- PowerShell：检查版本、创建环境、安装包、运行程序。
- VS Code：创建与编辑 `learning/hello_python.py`。
- 本阶段所有命令都在项目根目录执行；除安装检查外，应激活 `.venv`。

### 6. Lesson 01.1：打开 PowerShell并检查 Python

操作 1：按键盘 Windows 键，输入 `PowerShell`，点击 Windows PowerShell。不要在 Python `>>>` 提示符里输入 PowerShell 命令。

输入：

```powershell
python --version
```

`--version` 要求程序只报告版本。正常例子是 `Python 3.12.15`。本项目验证范围是 Python >=3.11,<3.13；3.12 最稳妥。若出现 Microsoft Store 或 “file cannot be accessed”，继续执行：

```powershell
where.exe python
```

它会列出候选路径。`WindowsApps\python.exe` 可能只是占位符。真正解释器常见于 `AppData\Local\Programs\Python`。若完全找不到 Python：浏览 `https://www.python.org/downloads/windows/`，选择 Python 3.12 64-bit installer；安装第一页勾选 `Add python.exe to PATH`，再选 Install Now。完成后关闭并重新打开 PowerShell，再检查版本。

检查 pip：

```powershell
python -m pip --version
```

这里使用 `python -m pip` 而不是裸 `pip`，可以确认 pip 属于同一个解释器。预期输出包含 pip 版本和 Python site-packages 路径。若提示 No module named pip，运行 `python -m ensurepip --upgrade`。

### 7. Lesson 01.2：安装并打开 VS Code

按 Windows 键搜索 `Visual Studio Code`。若没有，浏览 `https://code.visualstudio.com/` 下载 Windows User Installer。安装时建议勾选 Add to PATH、Open with Code 和 Register Code as an editor。

打开 VS Code，点击左侧 Extensions（四个方块），搜索 `Python`，确认发布者是 Microsoft，点击 Install。这个 extension 提供语法提示、解释器选择和调试，但它本身不是 Python。

创建项目文件夹时，本机策略要求 vibe coding 项目默认放在 `D:\BBB_vibecoding_project`；本教学仓库目前位于 `D:\AIROST\Intern-MachineLearning`，因为用户明确提供了现有工作区。学生的新副本可执行：

```powershell
New-Item -ItemType Directory -Path 'D:\BBB_vibecoding_project\personal-information-ner'
Set-Location 'D:\BBB_vibecoding_project\personal-information-ner'
```

`New-Item` 创建目录；`Set-Location` 改变当前目录。路径有连字符但无空格，单引号仍能避免 PowerShell 误解析。若 D: 不存在，先在 File Explorer 确认磁盘，或向老师询问允许的位置。

在 VS Code 点击 File -> Open Folder，选择项目目录，点击 Select Folder。点击 Terminal -> New Terminal。底部应出现 PowerShell，prompt 中路径应是项目根目录。输入：

```powershell
Get-Location
```

预期 Path 与打开的文件夹一致。若不一致，使用 `Set-Location` 修正。

### 8. Lesson 01.3：创建、激活并选择 Virtual Environment

在 VS Code Integrated Terminal、项目根目录执行：

```powershell
python -m venv .venv
```

命令成功通常没有大量输出，但 Explorer 会出现 `.venv`。如果 Access denied，确认项目不在受保护的 Program Files；如果找不到 venv，确认你用的是完整 python.org 安装。

激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

开头 `.` 表示当前目录，反斜线是 Windows 路径。成功后 prompt 前出现 `(.venv)`。若提示 execution policy 禁止脚本，只为当前 PowerShell 进程执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

`-Scope Process` 保证关闭窗口后失效，不永久降低系统安全设置。

验证：

```powershell
python -c "import sys; print(sys.executable)"
```

`-c` 执行引号里的短代码。预期路径以项目的 `.venv\Scripts\python.exe` 结尾。若仍是系统 Python，关闭终端，新建 PowerShell，再激活。

在 VS Code 按 Ctrl+Shift+P，输入 `Python: Select Interpreter`，选择包含 `.venv` 的条目。右下角状态栏应显示 `.venv`。Terminal 激活和编辑器解释器选择是两件事，两者都要确认。

### 9. Lesson 01.4：安装 uv、PyTorch 与依赖

本仓库用 `uv.lock` 锁定版本。若已安装 uv：

```powershell
uv --version
uv sync --all-groups
```

第一条只读；第二条读取 `pyproject.toml` 和 `uv.lock`，安装 runtime 与 dev dependencies。它会创建或更新 `.venv`。完整依赖包括 PyTorch 2.9.0、FastAPI、pypdf、pytest、ReportLab 等。

若没有 uv，可以先在已激活 `.venv` 使用：

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`install` 下载并安装；`-r` 表示从文件读取多项依赖。网络错误时检查校园代理；权限错误通常说明没有激活 `.venv`。不要用管理员权限掩盖路径错误。

验证关键依赖：

```powershell
python -c "import torch, fastapi, pypdf, pytest; print(torch.__version__); print(torch.cuda.is_available())"
```

本机真实验证版本是 Python 3.12.15、PyTorch 2.9.0+cpu；`cuda.is_available()` 为 False，项目按 CPU 设计。其他电脑的小版本可能不同，但必须满足 `pyproject.toml`。

### 9. Lesson 01.5：创建并运行第一个 Python 文件

在 VS Code Explorer 点击 New Folder，输入 `learning`；右键该目录 -> New File -> 输入 `hello_python.py`。第一行写 docstring：

```python
"""Phase 01 的第一个可运行 Python 程序。"""
```

Docstring 是给人和工具看的模块说明。接着逐行输入：

```python
import platform
import sys
```

`import` 加载模块。`platform` 提供系统/版本信息；`sys` 提供当前解释器路径。然后创建函数：

```python
def describe_environment() -> str:
    """返回当前 Python 与操作系统信息。"""
    return f"Python {platform.python_version()} | {platform.system()} | executable={sys.executable}"
```

`def` 定义函数；括号为空代表不接收参数；`-> str` 是返回类型提示；缩进的 `return` 把字符串交给调用者。f-string 用 `{表达式}` 插入值。

最后输入：

```python
if __name__ == "__main__":
    print("NER learning environment is ready.")
    print(describe_environment())
```

当直接运行文件时，`__name__` 是 `__main__`；当别的文件 import 它时，这两行不会自动打印。这让函数以后能被测试安全导入。

保存 Ctrl+S，在 Integrated Terminal 项目根目录运行：

```powershell
python learning\hello_python.py
```

本机实际输出结构：

```text
NER learning environment is ready.
Python 3.12.15 | Windows | executable=D:\...\Intern-MachineLearning\.venv\Scripts\python.exe
```

路径会因电脑不同而不同；关键是包含 `.venv`。

### 9. Lesson 01.6：退出与重新进入项目

退出环境：

```powershell
deactivate
```

`(.venv)` 从 prompt 消失，但 `.venv` 文件夹仍存在。第二天重新开发：打开 VS Code -> File/Open Recent -> 项目 -> Terminal/New Terminal -> 执行 `.\.venv\Scripts\Activate.ps1` -> `python --version` -> 运行 hello 文件。无需每天重建环境。

## 10. 完整代码回顾

阶段结束时 `learning/hello_python.py` 完整代码：

```python
"""Phase 01 的第一个可运行 Python 程序。"""

import platform
import sys


def describe_environment() -> str:
    """返回当前 Python 与操作系统信息，帮助学生确认解释器。"""
    return f"Python {platform.python_version()} | {platform.system()} | executable={sys.executable}"


if __name__ == "__main__":
    print("NER learning environment is ready.")
    print(describe_environment())
```

## 11. 跨文件调用关系

目前没有业务文件依赖它。Phase 01 的价值是验证所有后续文件共享同一解释器。测试未来可以 `from learning.hello_python import describe_environment`，此时 main guard 会阻止额外打印。

`.venv` 根据 `pyproject.toml`/`uv.lock` 安装包；Python extension 选择 `.venv\Scripts\python.exe`；Terminal 调用同一路径；源文件 import 已安装模块。

## 12. 数据流解释

`platform.python_version()` 返回 `str`；`platform.system()` 返回 `str`；`sys.executable` 是路径字符串。f-string 合并三个字符串，函数返回 `str`，`print` 把它发送到 terminal 标准输出。此阶段没有 Tensor。

## 13. 常见错误

1. `python` 打开 Store：使用 `where.exe python` 找真实安装并修复 PATH。
2. `Activate.ps1 cannot be loaded`：只对当前 Process 使用 Bypass。
3. `ModuleNotFoundError`：检查 `sys.executable` 是否指向 `.venv`，再安装包。
4. VS Code 有红线但终端能运行：编辑器没有选择 `.venv` interpreter。
5. `IndentationError`：函数体使用四个空格，不混 Tab。
6. 在 `>>>` 输入 PowerShell 命令：输入 `exit()` 回到 PowerShell。
7. 将 `.venv` 提交 Git：确认 `.gitignore` 包含 `.venv/`。

## 14. Checkpoint

在项目根目录、激活环境后运行：

```powershell
python --version
python -c "import sys; print(sys.executable)"
python learning\hello_python.py
python -c "import torch; print(torch.__version__)"
```

通过条件：Python 3.11/3.12；路径含 `.venv`; hello 打印 ready；torch 可 import。当前仓库真实执行：Python 3.12.15 和 PyTorch 2.9.0+cpu。任一失败先按第 13 节修复。

## 15. 学生练习

1. 给 `describe_environment` 增加 `platform.machine()`，观察 64-bit 架构文字。
2. 故意在函数缩进中删一个空格，读懂 IndentationError 后恢复。
3. 退出 `.venv`，比较 `sys.executable`，然后重新激活。
4. 用 `python -m pip list` 找出 torch 和 fastapi 版本。
5. 解释为什么不把 `.venv` 上传 GitHub。

## 16. 面试准备

简单英语："I use a project-specific virtual environment so dependency versions do not conflict with other projects. VS Code and PowerShell both use the same `.venv` interpreter. I verified Python 3.12 and the CPU build of PyTorch before writing model code."

## 17. 下一阶段预告

Phase 02 会在 `learning/python_foundations.py` 中学习 list、dict、function、class、object、inheritance、`self`、`super()` 和 type hint。这些知识会在 Phase 09 的 `nn.Module` 中逐项复用，而不是第一次看到模型类时才仓促解释。

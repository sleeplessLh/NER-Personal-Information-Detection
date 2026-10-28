# Phase 02：为机器学习补齐 Python 基础

## 1. 本阶段学习目标

本阶段创建 `learning/python_foundations.py`。你会用 NER 真实数据形式学习 list、dict、loop、function、parameter、return、class、object、inheritance、`self`、`__init__()`、`super()`、dataclass 与 type hint。结束时程序应打印 BIO 计数和实体字典。

这些概念现在学，是为了 Phase 09 看到 `class BiLSTMNER(nn.Module)` 时不同时承受 Python 和神经网络两层新知识。

## 2. 本阶段需要掌握的知识

- `list[str]`：有顺序、可重复的字符串集合。
- `dict[str, int]`：键到值的映射。
- function、parameter、argument、return value。
- class 是对象蓝图；object 是按蓝图创建的实例。
- inheritance 让子类获得父类行为。
- `self` 指当前对象；`super()` 访问父类。
- type hint 帮助阅读和静态检查，不会自动替你验证所有运行时数据。

## 3. 从零解释知识点

句子的 token 和 BIO label 都需要保持顺序，因此用 list。例如 `labels[0]` 是第一项。实体需要同时保存 text/type/start/end，使用 dict 可以按名字取值。函数把可重复逻辑命名；调用者传 argument，函数的 parameter 接收它，`return` 将结果交回调用者。

Class 像“实体说明书”，object 是一条具体实体。`self.name` 是每个 object 自己的数据。`__init__` 在创建 object 时运行。Inheritance 的语法是 `class Child(Parent)`。`super().__init__()` 调用父类初始化；在 PyTorch 中不调用它，`nn.Module` 可能无法登记层和参数。

Dataclass 自动生成保存字段所需的 `__init__` 等方法。因为 dataclass 与自定义父类同时使用，我们在 `__post_init__` 再调用父类初始化。

## 4. 本阶段开始前的项目状态

```text
learning/
  hello_python.py           [上一阶段已有]
  python_foundations.py     [本阶段新增]
tutorial/chapters/
  phase_00.md               [不变]
  phase_01.md               [不变]
  phase_02.md               [本阶段新增]
```

正式 `src/` 尚未开始；本阶段代码故意放 `learning/`，避免练习代码混进模型核心。

## 5. 本阶段需要使用的工具

打开 VS Code Explorer -> `learning` -> New File -> `python_foundations.py`。使用项目根目录 PowerShell，确认 `(.venv)` 和 `python -c "import sys; print(sys.executable)"` 指向项目环境。

### 6. Lesson 02.1：list、loop 与 dict

先输入：

```python
labels = ["B-PER", "O", "O", "B-ORG", "I-ORG"]
counts = {}
for label in labels:
    counts[label] = counts.get(label, 0) + 1
print(counts)
```

第一行创建五项 list。`for` 依次让变量 `label` 指向每项。`counts.get(label, 0)` 在 key 不存在时给 0，然后加 1。运行：

```powershell
python learning\python_foundations.py
```

临时版本实际应打印 `{'B-PER': 1, 'O': 2, 'B-ORG': 1, 'I-ORG': 1}`。若 `KeyError`，你可能写成 `counts[label] += 1`，但第一次还没有 key。

### 7. Lesson 02.2：把逻辑变成 function

把上面代码改为：

```python
def count_labels(labels: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    return counts
```

Function name 是 `count_labels`。Parameter name 是 `labels`，类型提示 `list[str]`。Return type 是 `dict[str,int]`。内部局部变量 `counts` 在调用结束后不应由外部直接修改。

调用示例：

```python
result = count_labels(["O", "B-PER", "O"])
assert result == {"O": 2, "B-PER": 1}
```

`assert` 在条件为 False 时抛出 AssertionError，很适合小型阶段测试。函数未来可由测试文件 import。

### 8. Lesson 02.3：class、object、self 与 `__init__`

继续输入：

```python
class NamedItem:
    def __init__(self, name: str) -> None:
        self.name = name
```

`NamedItem` 是 class name。调用 `NamedItem("Sarah")` 创建 object。Python 自动把 object 作为第一个 argument 传入 `self`，把 "Sarah" 传入 `name`。`self.name = name` 将参数保存为对象属性。

局部测试：

```python
person = NamedItem("Sarah")
assert person.name == "Sarah"
```

为什么不是普通函数？因为实体有持续状态，多个 method 要共享 name/type/span；对象把这些数据和行为放在一起。简单项目也可用 dict，但我们现在学习 class 是为了理解 PyTorch Module。

### 9. Lesson 02.4：inheritance 与 `super()`

先写最小子类：

```python
class Entity(NamedItem):
    def __init__(self, name: str, entity_type: str) -> None:
        super().__init__(name)
        self.entity_type = entity_type
```

括号里的 `NamedItem` 是父类。`super()` 返回一个代理，让当前子类调用父类实现。`super().__init__(name)` 负责建立 `self.name`；下一行建立新属性。若删掉 super 调用，`entity.name` 会不存在。

测试：

```python
entity = Entity("Sarah", "PER")
assert entity.name == "Sarah"
assert entity.entity_type == "PER"
```

与未来 PyTorch 的关系：`BiLSTMNER(nn.Module)` 继承 PyTorch 父类；`super().__init__()` 让父类准备参数、子模块、train/eval 状态等内部容器。

### 9. Lesson 02.5：dataclass 与半开区间

在 imports 加：

```python
from dataclasses import dataclass
```

将 Entity 改为：

```python
@dataclass
class Entity(NamedItem):
    name: str
    entity_type: str
    start: int
    end: int

    def __post_init__(self) -> None:
        super().__init__(self.name)
```

Decorator `@dataclass` 在 class 创建后增强它，自动生成接收四个字段的 constructor。半开区间 `[start,end)` 包含 start、不包含 end，所以原文实体可直接取 `text[start:end]`。

`__post_init__` 在 dataclass 自动初始化字段后运行，再调用父类。这里父类赋同一个 name，主要用于演示；正式模型不会使用这个 Entity class。

### 9. Lesson 02.6：method、union type 与 main guard

在 Entity 内加入：

```python
def as_dict(self) -> dict[str, str | int]:
    return {
        "text": self.name,
        "type": self.entity_type,
        "start": self.start,
        "end": self.end,
    }
```

这是 instance method，通过 `entity.as_dict()` 调用。返回值的 key 是 str；value 可能是 str 或 int，因此用 `str | int`。最后创建 `main()` 并用 main guard 调用，这与 Phase 01 原理相同。

运行实际最终版本：

```powershell
python learning\python_foundations.py
```

真实输出：

```text
{'B-PER': 1, 'O': 2, 'B-ORG': 1, 'I-ORG': 1}
{'text': 'Universiti Malaya', 'type': 'ORG', 'start': 15, 'end': 33}
```

## 10. 完整代码回顾

阶段结束时完整代码位于 `learning/python_foundations.py`，包括 import、`count_labels`、`NamedItem`、dataclass `Entity`、`as_dict`、`main` 和 main guard。请打开真实文件逐行比对，不要只复制片段。运行 `python -m py_compile learning\python_foundations.py` 可先检查语法。

## 11. 跨文件调用关系

`main()` 调用 `count_labels()` 和 `Entity(...)`；Entity 自动调用 dataclass constructor -> `__post_init__()` -> `NamedItem.__init__()`；随后 main 调用 `entity.as_dict()`。本阶段不 import `src/`，因此不会影响正式模型。

## 12. 数据流解释

labels 的类型是 `list[str]` -> `count_labels` 的 loop -> `dict[str,int]` -> print。构造 Entity 时四个 argument -> object fields -> `as_dict()` -> `dict[str,str|int]`。没有 Tensor；Python 类型是后续 Tensor 的上游原始数据。

## 13. 常见错误

1. `NameError: dataclass`：忘记 import。
2. `TypeError: missing argument`：构造 Entity 时字段数量不对。
3. `AttributeError: name`：普通继承版本忘记 `super().__init__`。
4. `IndentationError`：method 必须缩进在 class 内。
5. Function 打印但不 return：调用者得到 None；应使用 return。
6. 把 `self` 当用户参数传入：正常调用 `entity.as_dict()` 不写 self。

## 14. Checkpoint

执行：

```powershell
python -m py_compile learning\python_foundations.py
python learning\python_foundations.py
python -c "from learning.python_foundations import count_labels; assert count_labels(['O','O']) == {'O': 2}; print('PASS')"
```

通过条件：无语法错误、输出两个 dict、最后打印 PASS。本阶段真实执行结果将写入 snapshot manifest。

## 15. 学生练习

1. 给 Entity 添加 `length()`，返回 `end-start`。
2. 输入重复 PER 标签验证 count。
3. 暂时删除 super 调用，观察什么测试失败，然后恢复。
4. 把错误的 end=32 改成 33，解释半开区间。
5. 用自己的名字创建 PER object，但不要提交真实敏感数据。

## 16. 面试准备

"A class defines state and behavior, while an object is one instance. `self` refers to the current object. Inheritance lets a child reuse a parent. `super().__init__()` initializes the parent part. I learned these concepts before using PyTorch `nn.Module`."

## 17. 下一阶段预告

Phase 03 创建 `learning/bio_demo.py`，把 Python list/dict/function 用在真实 BIO 序列：验证标签、把 tags 转换成实体 span，并用具体英文句子解释 token 与 entity 的区别。

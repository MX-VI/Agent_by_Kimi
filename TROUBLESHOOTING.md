# Python 环境问题排查指南

## 问题：pip list 显示已安装 gradio，但运行时报 No module named 'gradio'

## 原因分析

这是典型的 **Python 环境不一致** 问题：
- `pip` 和 `python` 指向了不同的 Python 解释器
- 常见于多版本 Python 共存的情况

## 快速诊断

### 命令行用户
在 ai-agent 目录下运行 `check_env.bat`，查看输出。

### PyCharm 用户
右键运行 `check_env.py`，查看控制台输出。

## PyCharm 使用指南

### 1. 打开项目
- 打开 PyCharm
- File → Open → 选择 ai-agent 文件夹

### 2. 配置 Python 解释器
- File → Settings → Project: ai-agent → Python Interpreter
- 点击齿轮图标 → Add
- 选择 System Interpreter → 选择你的 Python 路径（如 `J:\PYTHON\python.exe`）
- 点击 OK

### 3. 检查环境
- 在项目视图中找到 `check_env.py`
- 右键 → Run 'check_env'
- 查看运行结果，根据提示修复问题

### 4. 安装依赖
如果 check_env 提示缺少依赖：

**方法一：使用 PyCharm 终端**
```
底部工具栏 → Terminal → 输入:
python -m pip install -r requirements.txt
```

**方法二：使用 PyCharm 包管理器**
```
File → Settings → Project → Python Interpreter
点击 + 号 → 搜索需要的包 → Install Package
```

### 5. 运行程序
- 右键 `main.py` → Run 'main'
- 或点击右上角运行按钮

## 常见情况及解决方案

### 情况 1：python 和 python3 命令混淆

**现象：**
```bash
pip install gradio        # 安装到了 Python 3.9
python main.py            # 使用的是 Python 3.11
```

**解决：**
```bash
# 统一使用 python3 和 pip3
python3 -m pip install gradio
python3 main.py

# 或者统一使用 python 和 pip
python -m pip install gradio
python main.py
```

### 情况 2：虚拟环境未激活

**现象：**
- 在项目外安装了包，但运行时没激活环境

**解决：**
```bash
# 如果使用 venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # Linux/Mac

# 然后再运行
python main.py
```

### 情况 3：多版本 Python 冲突

**现象：**
- 安装了 Anaconda，同时又有系统 Python
- pip 和 python 来自不同发行版

**解决：**
```bash
# 使用 Python 的 -m 参数指定 pip
python -m pip install gradio
python -m pip list

# 运行时也明确使用这个 python
python main.py
```

### 情况 4：IDE 使用的 Python 与终端不同

**现象：**
- VS Code/PyCharm 选择的解释器与 CMD 不同

**解决：**
- VS Code: 按 Ctrl+Shift+P → "Python: Select Interpreter" → 选择正确的环境
- PyCharm: File → Settings → Project → Python Interpreter

## 推荐的运行方式

### 方法 1：使用 Python -m（最可靠）

```bash
cd ai-agent

# 安装依赖
python -m pip install -r requirements.txt

# 运行程序
python main.py
```

### 方法 2：创建虚拟环境（推荐长期开发）

```bash
cd ai-agent

# 创建虚拟环境
python -m venv venv

# 激活环境
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py

# 退出环境
deactivate
```

### 方法 3：检查具体是哪个 Python

```bash
# 查看当前使用的 Python 路径
python -c "import sys; print(sys.executable)"

# 查看 pip 安装的包路径
pip show gradio | findstr "Location"

# 对比两者是否一致
```

## 修复脚本

如果以上方法都不奏效，运行这个强制修复：

```bash
# 找到你真正要用的 Python，然后重新安装
python -m pip uninstall gradio -y
python -m pip install gradio

# 验证
python -c "import gradio; print(gradio.__version__)"
```

## 验证步骤

1. 打开 CMD/PowerShell
2. 进入 ai-agent 目录：`cd 你的路径\ai-agent`
3. 运行诊断：`check_env.bat`
4. 根据输出选择对应的解决方案

## 如果还有问题

请提供以下信息：
1. `check_env.bat` 的完整输出
2. 运行 `main.py` 时的完整错误信息
3. 你使用的 IDE（如果有）

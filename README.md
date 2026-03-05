# Windows AI Agent

一个基于 DeepSeek API 的 AI Agent，支持文件操作、网页访问和内容总结。

## 功能特性

- 🤖 基于 DeepSeek AI 的智能对话
- 📁 本地文件操作（读/写/列目录）
- 🌐 网页访问和内容总结
- 🖥️ 两种图形界面可选（Gradio / Tkinter）
- ⚙️ 支持自定义配置

## 安装步骤

### 1. 环境要求
- Python 3.8+
- Windows 10/11

### 2. 安装依赖

**方案 A：使用 Tkinter 界面（推荐，无需额外安装）**
```bash
pip install -r requirements_minimal.txt
```

**方案 B：使用 Gradio 界面（需要额外依赖）**
```bash
pip install -r requirements.txt
```

### 3. 配置 API Key
编辑 `config.py` 文件，设置你的 DeepSeek API Key（已预填）。

### 4. 运行

**Tkinter 版本（轻量级）：**
```bash
python main_tkinter.py
```

**Gradio 版本（网页界面）：**
```bash
python main.py
```

## 使用说明

### 支持的命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `@read:路径` | 读取文件内容 | `@read:C:\Users\docs\note.txt` |
| `@write:路径\n内容` | 写入文件 | `@write:C:\test.txt\nHello World` |
| `@list:路径` | 列出目录 | `@list:C:\Users` |
| `@web:URL` | 访问并总结网页 | `@web:https://example.com` |
| `@cmd:命令` | 执行系统命令 | `@cmd:ipconfig`, `@cmd:dir` |

### JavaScript 渲染网站

对于使用 Vue/React 等前端框架的现代网站（如比亚迪官网），Agent 会自动使用 **Playwright** 渲染页面以获取完整内容。

如果提示需要安装 Playwright：
```bash
pip install playwright
playwright install chromium
```

### 示例对话

```
用户: @read:C:\Users\MyName\Desktop\notes.txt
Agent: 文件内容如下：...

用户: 总结一下 @web:https://news.example.com/article
Agent: 网页内容总结：...

用户: 把刚才的总结保存到桌面
Agent: 已保存到 C:\Users\MyName\Desktop\...
```

## 项目结构

```
ai-agent/
├── main.py                 # Gradio 界面版本
├── main_tkinter.py         # Tkinter 界面版本（无需 gradio）
├── agent.py                # Agent 核心逻辑
├── config.py               # 配置文件
├── requirements.txt        # Gradio 版本依赖
├── requirements_minimal.txt # 最小依赖（Tkinter 版本）
├── README.md               # 说明文档
├── check_env.py            # 环境检查脚本
├── TROUBLESHOOTING.md      # 问题排查指南
└── tools/
    ├── __init__.py
    ├── file_tool.py        # 文件操作工具
    └── web_tool.py         # 网页访问工具
```

## 界面选择

### Tkinter 版本（推荐）
- ✅ Python 内置，无需额外安装
- ✅ 轻量级，启动快
- ✅ 稳定可靠
- ⚠️ 界面相对简洁

### Gradio 版本
- ✅ 美观的网页风格界面
- ✅ 支持 Markdown 渲染
- ⚠️ 需要安装 gradio 和相关依赖
- ⚠️ 可能遇到 greenlet 编译问题

## 注意事项

- 文件操作请确保有相应权限
- 网页访问需要网络连接
- API 调用会产生费用，请注意使用量
- 推荐使用 **Tkinter 版本** 避免依赖问题
- **系统命令** (`@cmd:`) 请谨慎使用，已内置危险命令拦截保护

### 系统命令安全说明

Agent 支持执行系统命令 (`@cmd:命令`)，但有以下安全保护：

**完全禁止的危险命令：**
- `rm -rf /` 等破坏性命令
- `format` 等格式化命令
- `dd if=... of=/dev/...` 等磁盘操作

**使用建议：**
- 仅使用只读命令（如 `ipconfig`, `dir`, `systeminfo`）
- 避免使用修改系统或删除文件的命令
- 执行前请确认命令安全性

**常用安全命令示例：**
```
@cmd:ipconfig              - 查看网络配置
@cmd:dir C:\\Users          - 列出目录
@cmd:systeminfo            - 查看系统信息
@cmd:tasklist              - 查看进程列表
```

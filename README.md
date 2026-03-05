# Windows AI Agent

一个基于 DeepSeek API 的 AI Agent，支持文件操作、网页访问和内容总结。

## 功能特性

- 🤖 基于 DeepSeek AI 的智能对话
- 📁 本地文件操作（读/写/列目录）
- 🌐 网页访问和内容总结
- 🖥️ 美观的图形化界面
- ⚙️ 支持自定义配置

## 安装步骤

### 1. 环境要求
- Python 3.8+
- Windows 10/11

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器（用于访问现代网站）
```bash
playwright install chromium
```

### 4. 配置 API Key
编辑 `config.py` 文件，设置你的 DeepSeek API Key（已预填）。

### 5. 运行
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
├── main.py           # 主程序入口
├── agent.py          # Agent 核心逻辑
├── config.py         # 配置文件
├── requirements.txt  # 依赖列表
├── README.md         # 说明文档
└── tools/
    ├── __init__.py
    ├── file_tool.py  # 文件操作工具
    └── web_tool.py   # 网页访问工具
```

## 注意事项

- 文件操作请确保有相应权限
- 网页访问需要网络连接
- API 调用会产生费用，请注意使用量

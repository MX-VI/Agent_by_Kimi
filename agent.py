"""
AI Agent 核心逻辑
"""
import re
from openai import OpenAI
import config
from tools import FileTool, WebTool


class AIAgent:
    """AI Agent 主类"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL
        )
        self.file_tool = FileTool()
        self.web_tool = WebTool()
        self.conversation_history = []
        
        # 系统提示词
        self.system_prompt = """你是一个智能 AI Agent，可以帮助用户完成各种任务。

你可以使用以下工具（通过识别用户消息中的特殊命令）：

1. 文件操作：
   - @read:文件路径 - 读取文件内容
   - @write:文件路径\n内容 - 写入文件内容
   - @list:目录路径 - 列出目录内容

2. 网页访问：
   - @web:URL - 访问网页并获取内容

当检测到工具命令时，先执行工具，然后将结果整合到回复中。
如果用户要求总结网页内容，使用 @web:URL 获取内容后，提供简洁的总结。

请用中文回复用户。保持友好、专业的态度。"""
    
    def process_message(self, user_message: str) -> str:
        """处理用户消息"""
        # 检测并执行工具命令
        tool_results = []
        processed_message = user_message
        
        # 检测 @web:URL
        web_pattern = r'@web:(\S+)'
        web_matches = re.findall(web_pattern, user_message)
        for url in web_matches:
            result = self.web_tool.summarize_webpage(url)
            tool_results.append(f"【网页访问结果 - {url}】\n{result}")
            processed_message = processed_message.replace(f"@web:{url}", f"[已访问网页: {url}]")
        
        # 检测 @read:路径
        read_pattern = r'@read:(.+?)(?=\s|$|@)'
        read_matches = re.findall(read_pattern, user_message)
        for file_path in read_matches:
            file_path = file_path.strip()
            result = self.file_tool.read_file(file_path)
            tool_results.append(f"【文件读取结果】\n{result}")
            processed_message = processed_message.replace(f"@read:{file_path}", f"[已读取文件: {file_path}]")
        
        # 检测 @write:路径\n内容
        write_pattern = r'@write:(.+?)\n(.+?)(?=\n@|\n\n|$)'
        write_matches = re.findall(write_pattern, user_message, re.DOTALL)
        for file_path, content in write_matches:
            result = self.file_tool.write_file(file_path.strip(), content.strip())
            tool_results.append(f"【文件写入结果】\n{result}")
            processed_message = processed_message.replace(f"@write:{file_path}\n{content}", f"[已写入文件: {file_path}]")
        
        # 检测 @list:路径
        list_pattern = r'@list:(.+?)(?=\s|$|@)'
        list_matches = re.findall(list_pattern, user_message)
        for dir_path in list_matches:
            dir_path = dir_path.strip()
            result = self.file_tool.list_directory(dir_path)
            tool_results.append(f"【目录列表结果】\n{result}")
            processed_message = processed_message.replace(f"@list:{dir_path}", f"[已列出目录: {dir_path}]")
        
        # 构建完整提示
        full_prompt = processed_message
        if tool_results:
            full_prompt += "\n\n" + "\n\n".join(tool_results)
        
        # 添加到对话历史
        self.conversation_history.append({"role": "user", "content": full_prompt})
        
        # 调用 DeepSeek API
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            # 只保留最近 10 轮对话
            messages.extend(self.conversation_history[-20:])
            
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE
            )
            
            ai_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            error_msg = f"❌ AI 调用出错：{str(e)}"
            return error_msg
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        return "✅ 对话历史已清空"

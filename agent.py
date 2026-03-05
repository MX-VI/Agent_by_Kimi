"""
AI Agent 核心逻辑 - 带超时控制和思考过程显示
"""
import re
import sys
import concurrent.futures
from openai import OpenAI
import config
from tools import FileTool, WebTool, CommandTool


# 全局超时设置（秒）
OPERATION_TIMEOUT = 30


class TimeoutError(Exception):
    """操作超时异常"""
    pass


def run_with_timeout(func, timeout_sec, *args, **kwargs):
    """在指定时间内执行函数，超时则抛出 TimeoutError"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_sec)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"操作超过 {timeout_sec} 秒未响应")


class AIAgent:
    """AI Agent 主类"""
    
    def __init__(self, think_callback=None):
        """
        初始化 Agent
        
        Args:
            think_callback: 思考过程回调函数，接收 (step, message) 参数
        """
        self.client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL
        )
        self.file_tool = FileTool()
        self.web_tool = WebTool()
        self.command_tool = CommandTool()
        self.conversation_history = []
        self.think_callback = think_callback
        
        # 系统提示词
        self.system_prompt = """你是一个智能 AI Agent，可以帮助用户完成各种任务。

你可以使用以下工具（通过识别用户消息中的特殊命令）：

1. 文件操作：
   - @read:文件路径 - 读取文件内容
   - @write:文件路径\n内容 - 写入文件内容
   - @list:目录路径 - 列出目录内容

2. 网页访问：
   - @web:URL - 访问网页并获取内容

3. 系统命令（谨慎使用）：
   - @cmd:命令 - 执行系统命令（如 @cmd:dir, @cmd:ipconfig）

当检测到工具命令时，先执行工具，然后将结果整合到回复中。
如果用户要求总结网页内容，使用 @web:URL 获取内容后，提供简洁的总结。

请用中文回复用户。保持友好、专业的态度。"""
    
    def _think(self, step: str, message: str):
        """
        输出思考过程
        
        Args:
            step: 步骤名称
            message: 思考内容
        """
        if self.think_callback:
            self.think_callback(step, message)
    
    def _execute_tools(self, user_message):
        """执行工具命令（内部方法）"""
        tool_results = []
        processed_message = user_message
        executed_tools = []
        
        # 检测 @web:URL
        web_pattern = r'@web:(\S+)'
        web_matches = re.findall(web_pattern, user_message)
        if web_matches:
            self._think("🔍 命令识别", f"检测到 {len(web_matches)} 个网页访问命令")
        
        for i, url in enumerate(web_matches, 1):
            self._think("🌐 网页访问", f"[{i}/{len(web_matches)}] 正在访问: {url}")
            try:
                result = self.web_tool.summarize_webpage(url)
                tool_results.append(f"【网页访问结果 - {url}】\n{result}")
                processed_message = processed_message.replace(f"@web:{url}", f"[已访问网页: {url}]")
                executed_tools.append(f"网页访问: {url}")
                self._think("✅ 网页访问完成", f"成功获取 {url} 的内容")
            except Exception as e:
                error_msg = f"❌ 访问失败: {str(e)}"
                tool_results.append(f"【网页访问结果 - {url}】\n{error_msg}")
                self._think("❌ 网页访问失败", f"{url}: {str(e)}")
        
        # 检测 @read:路径
        read_pattern = r'@read:(.+?)(?=\s|$|@)'
        read_matches = re.findall(read_pattern, user_message)
        if read_matches:
            self._think("🔍 命令识别", f"检测到 {len(read_matches)} 个文件读取命令")
        
        for i, file_path in enumerate(read_matches, 1):
            file_path = file_path.strip()
            self._think("📄 文件读取", f"[{i}/{len(read_matches)}] 正在读取: {file_path}")
            try:
                result = self.file_tool.read_file(file_path)
                tool_results.append(f"【文件读取结果】\n{result}")
                processed_message = processed_message.replace(f"@read:{file_path}", f"[已读取文件: {file_path}]")
                executed_tools.append(f"文件读取: {file_path}")
                self._think("✅ 文件读取完成", f"成功读取 {file_path}")
            except Exception as e:
                error_msg = f"❌ 读取失败: {str(e)}"
                tool_results.append(f"【文件读取结果】\n{error_msg}")
                self._think("❌ 文件读取失败", f"{file_path}: {str(e)}")
        
        # 检测 @write:路径\n内容
        write_pattern = r'@write:(.+?)\n(.+?)(?=\n@|\n\n|$)'
        write_matches = re.findall(write_pattern, user_message, re.DOTALL)
        if write_matches:
            self._think("🔍 命令识别", f"检测到 {len(write_matches)} 个文件写入命令")
        
        for i, (file_path, content) in enumerate(write_matches, 1):
            self._think("📝 文件写入", f"[{i}/{len(write_matches)}] 正在写入: {file_path}")
            try:
                result = self.file_tool.write_file(file_path.strip(), content.strip())
                tool_results.append(f"【文件写入结果】\n{result}")
                processed_message = processed_message.replace(f"@write:{file_path}\n{content}", f"[已写入文件: {file_path}]")
                executed_tools.append(f"文件写入: {file_path}")
                self._think("✅ 文件写入完成", f"成功写入 {file_path}")
            except Exception as e:
                error_msg = f"❌ 写入失败: {str(e)}"
                tool_results.append(f"【文件写入结果】\n{error_msg}")
                self._think("❌ 文件写入失败", f"{file_path}: {str(e)}")
        
        # 检测 @list:路径
        list_pattern = r'@list:(.+?)(?=\s|$|@)'
        list_matches = re.findall(list_pattern, user_message)
        if list_matches:
            self._think("🔍 命令识别", f"检测到 {len(list_matches)} 个目录列表命令")
        
        for i, dir_path in enumerate(list_matches, 1):
            dir_path = dir_path.strip()
            self._think("📂 目录列表", f"[{i}/{len(list_matches)}] 正在列出: {dir_path}")
            try:
                result = self.file_tool.list_directory(dir_path)
                tool_results.append(f"【目录列表结果】\n{result}")
                processed_message = processed_message.replace(f"@list:{dir_path}", f"[已列出目录: {dir_path}]")
                executed_tools.append(f"目录列表: {dir_path}")
                self._think("✅ 目录列表完成", f"成功列出 {dir_path}")
            except Exception as e:
                error_msg = f"❌ 列出失败: {str(e)}"
                tool_results.append(f"【目录列表结果】\n{error_msg}")
                self._think("❌ 目录列表失败", f"{dir_path}: {str(e)}")
        
        # 检测 @cmd:命令
        cmd_pattern = r'@cmd:(.+?)(?=\n|$|@)'
        cmd_matches = re.findall(cmd_pattern, user_message)
        if cmd_matches:
            self._think("🔍 命令识别", f"检测到 {len(cmd_matches)} 个系统命令")
        
        for i, command in enumerate(cmd_matches, 1):
            command = command.strip()
            self._think("⚡ 系统命令", f"[{i}/{len(cmd_matches)}] 正在执行: {command}")
            try:
                result = self.command_tool.execute(command, timeout=OPERATION_TIMEOUT)
                tool_results.append(f"【系统命令结果】\n{result}")
                processed_message = processed_message.replace(f"@cmd:{command}", f"[已执行命令: {command}]")
                executed_tools.append(f"系统命令: {command}")
                self._think("✅ 系统命令完成", f"成功执行 {command}")
            except Exception as e:
                error_msg = f"❌ 执行失败: {str(e)}"
                tool_results.append(f"【系统命令结果】\n{error_msg}")
                self._think("❌ 系统命令失败", f"{command}: {str(e)}")
        
        # 总结执行的工具
        if executed_tools:
            self._think("📋 工具执行总结", f"共执行 {len(executed_tools)} 个工具:\n" + 
                       "\n".join([f"  • {t}" for t in executed_tools]))
        else:
            self._think("💬 直接对话", "未检测到工具命令，直接进入 AI 对话模式")
        
        return processed_message, tool_results
    
    def _call_api(self, full_prompt):
        """调用 AI API（内部方法）"""
        # 添加到对话历史
        self.conversation_history.append({"role": "user", "content": full_prompt})
        
        messages = [{"role": "system", "content": self.system_prompt}]
        # 只保留最近 10 轮对话
        messages.extend(self.conversation_history[-20:])
        
        self._think("🤖 AI 思考", "正在调用 DeepSeek API 生成回复...")
        
        response = self.client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
            timeout=OPERATION_TIMEOUT
        )
        
        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        self._think("✅ AI 回复完成", f"生成回复 ({len(ai_response)} 字符)")
        
        return ai_response
    
    def process_message(self, user_message: str, think_callback=None) -> str:
        """
        处理用户消息（带 30 秒超时保护和思考过程显示）
        
        Args:
            user_message: 用户输入的消息
            think_callback: 可选的思考过程回调函数
            
        Returns:
            AI 回复或错误信息
        """
        # 临时设置回调
        if think_callback:
            self.think_callback = think_callback
        
        self._think("🚀 开始处理", f"用户输入: {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
        
        try:
            # 步骤 1: 执行工具命令（30秒超时）
            self._think("⏱️ 阶段 1/2", "执行工具命令（30秒超时）...")
            try:
                processed_message, tool_results = run_with_timeout(
                    self._execute_tools, 
                    OPERATION_TIMEOUT, 
                    user_message
                )
            except TimeoutError:
                self._think("❌ 超时", f"工具执行超过 {OPERATION_TIMEOUT} 秒")
                return f"❌ 操作超时（{OPERATION_TIMEOUT}秒）：工具执行时间过长，请检查网络连接或文件路径"
            except Exception as e:
                self._think("❌ 错误", f"工具执行错误: {str(e)}")
                return f"❌ 工具执行错误：{str(e)}"
            
            # 构建完整提示
            full_prompt = processed_message
            if tool_results:
                full_prompt += "\n\n" + "\n\n".join(tool_results)
                self._think("📝 提示构建", f"已整合 {len(tool_results)} 个工具结果")
            
            # 步骤 2: 调用 AI API（30秒超时）
            self._think("⏱️ 阶段 2/2", "调用 AI API 生成回复（30秒超时）...")
            try:
                ai_response = run_with_timeout(
                    self._call_api,
                    OPERATION_TIMEOUT,
                    full_prompt
                )
                self._think("🎉 处理完成", "消息处理完毕")
                return ai_response + "\n\n---\n✅ 完毕"
                
            except TimeoutError:
                self._think("❌ 超时", f"AI API 调用超过 {OPERATION_TIMEOUT} 秒")
                return f"❌ AI 响应超时（{OPERATION_TIMEOUT}秒）：DeepSeek API 未在指定时间内响应，请稍后重试"
            except Exception as e:
                self._think("❌ 错误", f"AI 调用错误: {str(e)}")
                return f"❌ AI 调用出错：{str(e)}"
                
        except Exception as e:
            self._think("❌ 系统错误", f"未预期错误: {str(e)}")
            return f"❌ 系统错误：{str(e)}"
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        return "✅ 对话历史已清空"

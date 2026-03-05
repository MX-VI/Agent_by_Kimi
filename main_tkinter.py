"""
AI Agent 主程序入口 - Tkinter GUI 版本
无需安装 gradio，使用 Python 内置 tkinter
支持思考过程显示
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import config
from agent import AIAgent


class AIAgentGUI:
    """AI Agent 图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(1000, 700)
        
        # 创建 Agent，传入思考过程回调
        self.agent = AIAgent(think_callback=self.on_think)
        
        # 消息队列用于线程间通信
        self.msg_queue = queue.Queue()
        self.think_queue = queue.Queue()
        
        # 创建界面
        self.create_widgets()
        
        # 启动队列检查
        self.check_queues()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主分割面板
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ===== 左侧：对话区域 =====
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=3)
        
        # 顶部说明
        header_frame = ttk.Frame(left_frame, padding="5")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(
            header_frame, 
            text="🤖 AI Agent - DeepSeek",
            font=("微软雅黑", 16, "bold")
        ).pack(anchor=tk.W)
        
        ttk.Label(
            header_frame,
            text="支持命令: @read:路径  @write:路径\\n内容  @list:路径  @web:URL  @cmd:命令",
            font=("微软雅黑", 9),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(3, 0))
        
        # 对话显示区
        chat_frame = ttk.LabelFrame(left_frame, text="对话记录", padding="5")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            padx=8,
            pady=8,
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # 输入区
        input_frame = ttk.Frame(left_frame, padding="5")
        input_frame.pack(fill=tk.X)
        
        self.input_box = ttk.Entry(input_frame, font=("微软雅黑", 11))
        self.input_box.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        self.input_box.bind("<Return>", self.on_send)
        self.input_box.focus()
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="发送",
            command=self.on_send,
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="清空",
            command=self.on_clear,
            width=6
        ).pack(side=tk.LEFT)
        
        # 快捷按钮
        shortcut_frame = ttk.Frame(left_frame, padding="5")
        shortcut_frame.pack(fill=tk.X)
        
        ttk.Button(
            shortcut_frame,
            text="📄 读取文件",
            command=lambda: self.set_input("@read:C:\\\\Windows\\\\System32\\\\drivers\\\\etc\\\\hosts")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            shortcut_frame,
            text="🌐 访问网页",
            command=lambda: self.set_input("总结一下 @web:https://www.deepseek.com")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            shortcut_frame,
            text="⚡ 系统命令",
            command=lambda: self.set_input("@cmd:ipconfig")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            shortcut_frame,
            text="🧹 清空思考",
            command=self.on_clear_think
        ).pack(side=tk.RIGHT)
        
        # ===== 右侧：思考过程区域 =====
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        think_frame = ttk.LabelFrame(right_frame, text="🧠 思考过程", padding="5")
        think_frame.pack(fill=tk.BOTH, expand=True)
        
        self.think_display = scrolledtext.ScrolledText(
            think_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            padx=5,
            pady=5,
            bg="#f5f5f5",
            fg="#333333"
        )
        self.think_display.pack(fill=tk.BOTH, expand=True)
        self.think_display.config(state=tk.DISABLED)
        
        # 状态栏
        self.status_bar = ttk.Label(
            self.root,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def set_input(self, text):
        """设置输入框内容"""
        self.input_box.delete(0, tk.END)
        self.input_box.insert(0, text)
        self.input_box.focus()
    
    def add_message(self, role, content):
        """添加消息到对话区"""
        self.chat_display.config(state=tk.NORMAL)
        
        if role == "user":
            self.chat_display.insert(tk.END, f"\n👤 你:\n", "user")
            self.chat_display.insert(tk.END, f"{content}\n")
        else:
            self.chat_display.insert(tk.END, f"\n🤖 Agent:\n", "agent")
            self.chat_display.insert(tk.END, f"{content}\n")
        
        self.chat_display.tag_config("user", foreground="#0066cc", font=("微软雅黑", 9, "bold"))
        self.chat_display.tag_config("agent", foreground="#009900", font=("微软雅黑", 9, "bold"))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def add_think(self, step: str, message: str):
        """添加思考过程"""
        self.think_display.config(state=tk.NORMAL)
        
        # 根据步骤类型设置颜色
        if "❌" in step or "错误" in step or "失败" in message:
            color = "#cc0000"  # 红色
        elif "✅" in step or "完成" in step:
            color = "#009900"  # 绿色
        elif "⏱️" in step:
            color = "#ff6600"  # 橙色
        elif "🔍" in step or "识别" in step:
            color = "#0066cc"  # 蓝色
        else:
            color = "#666666"  # 灰色
        
        timestamp = self.get_timestamp()
        self.think_display.insert(tk.END, f"[{timestamp}] ", "time")
        self.think_display.insert(tk.END, f"{step}\n", ("step",))
        self.think_display.insert(tk.END, f"  {message}\n\n", ("message",))
        
        self.think_display.tag_config("time", foreground="#999999", font=("Consolas", 8))
        self.think_display.tag_config("step", foreground=color, font=("微软雅黑", 9, "bold"))
        self.think_display.tag_config("message", foreground="#333333", font=("Consolas", 9))
        
        self.think_display.see(tk.END)
        self.think_display.config(state=tk.DISABLED)
    
    def get_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def on_think(self, step: str, message: str):
        """思考过程回调（在主线程中调用）"""
        self.think_queue.put((step, message))
    
    def on_send(self, event=None):
        """发送消息"""
        message = self.input_box.get().strip()
        if not message:
            return
        
        self.input_box.delete(0, tk.END)
        self.add_message("user", message)
        self.status_bar.config(text="Agent 正在思考...")
        
        # 清空上一次思考过程
        self.on_clear_think()
        self.add_think("🚀 开始处理", f"用户输入: {message[:80]}{'...' if len(message) > 80 else ''}")
        
        # 在后台线程处理
        thread = threading.Thread(target=self.process_message, args=(message,))
        thread.daemon = True
        thread.start()
    
    def process_message(self, message):
        """处理消息（在后台线程）"""
        try:
            response = self.agent.process_message(message)
            self.msg_queue.put(("response", response))
        except Exception as e:
            self.msg_queue.put(("error", str(e)))
    
    def check_queues(self):
        """检查消息队列"""
        # 检查主消息队列
        try:
            while True:
                msg_type, content = self.msg_queue.get_nowait()
                if msg_type == "response":
                    self.add_message("agent", content)
                    self.status_bar.config(text="就绪")
                elif msg_type == "error":
                    self.add_message("agent", f"❌ 错误: {content}")
                    self.status_bar.config(text="发生错误")
        except queue.Empty:
            pass
        
        # 检查思考队列
        try:
            while True:
                step, message = self.think_queue.get_nowait()
                self.add_think(step, message)
        except queue.Empty:
            pass
        
        self.root.after(50, self.check_queues)
    
    def on_clear(self):
        """清空对话"""
        if messagebox.askyesno("确认", "确定要清空所有对话吗？"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.agent.clear_history()
    
    def on_clear_think(self):
        """清空思考过程"""
        self.think_display.config(state=tk.NORMAL)
        self.think_display.delete(1.0, tk.END)
        self.think_display.config(state=tk.DISABLED)


def main():
    """主函数"""
    print("="*50)
    print("🤖 AI Agent 启动中...")
    print(f"模型：{config.MODEL_NAME}")
    print(f"API：{config.DEEPSEEK_BASE_URL}")
    print("="*50)
    
    root = tk.Tk()
    app = AIAgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

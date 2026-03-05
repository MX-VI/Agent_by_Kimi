"""
AI Agent 主程序入口 - Tkinter GUI 版本
无需安装 gradio，使用 Python 内置 tkinter
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
        self.root.minsize(800, 600)
        
        # 创建 Agent
        self.agent = AIAgent()
        
        # 消息队列用于线程间通信
        self.msg_queue = queue.Queue()
        
        # 创建界面
        self.create_widgets()
        
        # 启动队列检查
        self.check_queue()
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部说明
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(
            header_frame, 
            text="🤖 AI Agent - DeepSeek",
            font=("微软雅黑", 16, "bold")
        ).pack(anchor=tk.W)
        
        ttk.Label(
            header_frame,
            text="支持命令: @read:路径  @write:路径\\n内容  @list:路径  @web:URL  @cmd:命令",
            font=("微软雅黑", 10),
            foreground="gray"
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # 对话显示区
        chat_frame = ttk.Frame(self.root, padding="10")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # 输入区
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.input_box = ttk.Entry(input_frame, font=("微软雅黑", 11))
        self.input_box.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        self.input_box.bind("<Return>", self.on_send)
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            btn_frame,
            text="发送",
            command=self.on_send,
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_frame,
            text="清空",
            command=self.on_clear,
            width=8
        ).pack(side=tk.LEFT)
        
        # 状态栏
        self.status_bar = ttk.Label(
            self.root,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 添加快捷按钮
        shortcut_frame = ttk.Frame(self.root, padding="0 0 10 10")
        shortcut_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(
            shortcut_frame,
            text="📄 示例：读取文件",
            command=lambda: self.set_input("@read:C:\\\\Windows\\\\System32\\\\drivers\\\\etc\\\\hosts")
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Button(
            shortcut_frame,
            text="🌐 示例：访问网页",
            command=lambda: self.set_input("总结一下 @web:https://www.deepseek.com")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            shortcut_frame,
            text="⚡ 示例：系统命令",
            command=lambda: self.set_input("@cmd:ipconfig")
        ).pack(side=tk.LEFT)
    
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
        
        self.chat_display.tag_config("user", foreground="#0066cc", font=("微软雅黑", 10, "bold"))
        self.chat_display.tag_config("agent", foreground="#009900", font=("微软雅黑", 10, "bold"))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def on_send(self, event=None):
        """发送消息"""
        message = self.input_box.get().strip()
        if not message:
            return
        
        self.input_box.delete(0, tk.END)
        self.add_message("user", message)
        self.status_bar.config(text="Agent 思考中...")
        
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
    
    def check_queue(self):
        """检查消息队列"""
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
        
        self.root.after(100, self.check_queue)
    
    def on_clear(self):
        """清空对话"""
        if messagebox.askyesno("确认", "确定要清空所有对话吗？"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.agent.clear_history()


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

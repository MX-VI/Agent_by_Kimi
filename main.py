"""
AI Agent 主程序入口
图形化界面使用 Gradio
"""
import gradio as gr
import markdown
from agent import AIAgent
import config


# 创建全局 Agent 实例
agent = AIAgent()


def respond(message, chat_history):
    """处理用户输入并返回回复"""
    if not message.strip():
        return "", chat_history
    
    # 显示用户消息
    chat_history.append([message, "思考中..."])
    yield "", chat_history
    
    # 获取 AI 回复
    response = agent.process_message(message)
    
    # 更新最后一条消息
    chat_history[-1][1] = response
    yield "", chat_history


def clear_chat():
    """清空对话"""
    agent.clear_history()
    return None, []


def create_ui():
    """创建 Gradio 界面"""
    
    # 自定义 CSS
    custom_css = """
    .chatbot {
        height: 600px;
    }
    .input-box {
        border-radius: 10px;
    }
    """
    
    with gr.Blocks(css=custom_css, title=config.WINDOW_TITLE) as demo:
        gr.Markdown(f"""
        # 🤖 AI Agent - DeepSeek
        
        一个智能 AI 助手，支持文件操作和网页访问。
        
        **快捷命令：**
        - `@read:C:\\path\\to\\file.txt` - 读取文件
        - `@write:C:\\path\\to\\file.txt\\n内容` - 写入文件
        - `@list:C:\\path\\to\\dir` - 列出目录
        - `@web:https://example.com` - 访问网页
        """)
        
        chatbot = gr.Chatbot(
            label="对话",
            height=600,
            bubble_full_width=False
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                label="输入消息",
                placeholder="输入消息或使用命令 @read: @write: @list: @web:",
                scale=8,
                lines=2
            )
            submit_btn = gr.Button("发送", scale=1, variant="primary")
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ 清空对话", scale=1)
            example1 = gr.Button("📄 示例：读取文件", scale=1)
            example2 = gr.Button("🌐 示例：访问网页", scale=1)
        
        # 事件绑定
        submit_btn.click(
            respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )
        
        msg_input.submit(
            respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[msg_input, chatbot]
        )
        
        example1.click(
            lambda: "@read:C:\\Windows\\System32\\drivers\\etc\\hosts",
            outputs=msg_input
        )
        
        example2.click(
            lambda: "总结一下 @web:https://www.deepseek.com",
            outputs=msg_input
        )
        
        gr.Markdown("""
        ---
        💡 **提示：** 输入命令后按 Enter 发送，支持 Markdown 格式显示
        """)
    
    return demo


def main():
    """主函数"""
    print("="*50)
    print("🤖 AI Agent 启动中...")
    print(f"模型：{config.MODEL_NAME}")
    print(f"API：{config.DEEPSEEK_BASE_URL}")
    print("="*50)
    
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()

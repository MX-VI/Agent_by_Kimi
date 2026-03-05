"""
网页访问工具模块（增强版）
支持 JavaScript 渲染
"""
import re
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import config


class WebTool:
    """网页访问工具类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
    
    def fetch_url(self, url: str) -> str:
        """获取网页内容"""
        try:
            # 添加协议头
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # 验证 URL
            parsed = urlparse(url)
            if not parsed.netloc:
                return f"❌ 错误：无效的 URL - {url}"
            
            # 发送请求
            response = self.session.get(url, timeout=config.WEB_TIMEOUT)
            response.raise_for_status()
            
            # 检测编码
            response.encoding = response.apparent_encoding
            
            return response.text
        except requests.exceptions.Timeout:
            return f"❌ 错误：请求超时（{config.WEB_TIMEOUT}秒）"
        except requests.exceptions.ConnectionError:
            return f"❌ 错误：无法连接到服务器"
        except requests.exceptions.HTTPError as e:
            return f"❌ 错误：HTTP {e.response.status_code}"
        except Exception as e:
            return f"❌ 访问网页时出错：{str(e)}"
    
    def fetch_with_js(self, url: str, wait_time: int = 3) -> str:
        """
        使用 Playwright 获取 JavaScript 渲染后的页面内容
        需要安装：pip install playwright && playwright install chromium
        """
        try:
            from playwright.sync_api import sync_playwright
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent=config.USER_AGENT
                )
                page.goto(url, wait_until='networkidle', timeout=config.WEB_TIMEOUT*1000)
                page.wait_for_timeout(wait_time * 1000)  # 额外等待 JS 渲染
                
                html = page.content()
                browser.close()
                return html
                
        except ImportError:
            return None  # 返回 None 表示需要回退到普通请求
        except Exception as e:
            return f"❌ 渲染页面时出错：{str(e)}"
    
    def extract_content(self, html: str, is_js_rendered: bool = False) -> str:
        """从 HTML 中提取主要内容"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # 获取标题
            title = ""
            if soup.title:
                title = soup.title.get_text(strip=True)
            
            # 尝试找到主要内容
            main_content = ""
            
            # 对于 JS 渲染的网站，尝试更多选择器
            selectors = ['article', 'main', '[role="main"]', '.content', '.post', 
                        '.entry', '#app', '#root', '.app', '.main', 'body']
            
            for selector in selectors:
                if selector.startswith('#') or selector.startswith('.'):
                    content = soup.select_one(selector)
                else:
                    content = soup.find(selector) if selector in ['article', 'main', 'body'] else soup.select_one(selector)
                
                if content and len(content.get_text(strip=True)) > 100:
                    main_content = content.get_text(separator='\n', strip=True)
                    break
            
            # 清理文本
            lines = [line.strip() for line in main_content.split('\n') if line.strip()]
            main_content = '\n'.join(lines)
            
            # 移除模板变量（如 {{item.title}}）
            main_content = re.sub(r'\{\{[^}]+\}\}', '', main_content)
            
            # 限制长度
            max_len = 15000
            if len(main_content) > max_len:
                main_content = main_content[:max_len] + "\n\n... [内容已截断]"
            
            result = []
            if title:
                result.append(f"标题：{title}")
                result.append("="*50)
            result.append(main_content)
            
            return '\n'.join(result)
        except Exception as e:
            return f"❌ 提取内容时出错：{str(e)}"
    
    def summarize_webpage(self, url: str, use_js: bool = True) -> str:
        """
        获取并返回网页内容
        use_js=True 时尝试使用 Playwright 渲染 JavaScript（推荐用于现代网站）
        """
        html = None
        is_js_rendered = False
        
        # 如果允许使用 JS，先尝试
        if use_js:
            html = self.fetch_with_js(url)
            if html is None:
                # Playwright 未安装，回退到普通请求
                html = self.fetch_url(url)
                is_js_rendered = False
            elif not html.startswith("❌"):
                is_js_rendered = True
            else:
                # JS 渲染出错，尝试普通请求
                html = self.fetch_url(url)
                is_js_rendered = False
        else:
            html = self.fetch_url(url)
        
        if html.startswith("❌"):
            return html
        
        content = self.extract_content(html, is_js_rendered)
        
        # 如果内容太少，可能是 JS 渲染网站但用普通方式获取了
        if len(content) < 200 and not is_js_rendered:
            return "⚠️ 提示：该网站可能需要 JavaScript 渲染。\n" \
                   "如需访问动态网站，请安装 Playwright：\n" \
                   f"  {sys.executable} -m pip install playwright\n" \
                   f"  {sys.executable} -m playwright install chromium\n\n" \
                   "当前获取到的内容：\n" + content
        
        return content


def validate_url(url: str) -> bool:
    """验证 URL 格式"""
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))

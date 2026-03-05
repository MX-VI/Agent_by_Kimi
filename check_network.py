#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 网络诊断脚本
用于排查 AI Agent 网页访问问题
"""

import sys
import socket
import ssl
import urllib.request
import urllib.error
import subprocess
import os
from pathlib import Path


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_result(status, message):
    icon = "✅" if status else "❌"
    print(f"  {icon} {message}")


def check_python_env():
    """检查 Python 环境"""
    print_section("Python 环境检查")
    print(f"  Python 版本: {sys.version}")
    print(f"  Python 路径: {sys.executable}")
    print(f"  平台: {sys.platform}")
    
    # 检查是否是 Windows
    if sys.platform == "win32":
        print_result(True, "Windows 平台")
    else:
        print_result(False, f"非 Windows 平台: {sys.platform}")
    
    return True


def check_dependencies():
    """检查必要的依赖包"""
    print_section("依赖包检查")
    
    deps = {
        "requests": "HTTP 请求库",
        "bs4": "HTML 解析 (BeautifulSoup)",
        "urllib": "内置 URL 库",
    }
    
    all_ok = True
    for module, desc in deps.items():
        try:
            if module == "bs4":
                __import__("bs4")
                print_result(True, f"{module}: {desc}")
            elif module == "urllib":
                __import__("urllib.request")
                print_result(True, f"{module}: {desc}")
            else:
                mod = __import__(module)
                version = getattr(mod, "__version__", "unknown")
                print_result(True, f"{module}: {desc} (v{version})")
        except ImportError:
            print_result(False, f"{module}: {desc} - 未安装!")
            all_ok = False
    
    return all_ok


def check_dns_resolution():
    """检查 DNS 解析"""
    print_section("DNS 解析检查")
    
    test_hosts = [
        ("www.baidu.com", "百度"),
        ("www.byd.com", "比亚迪官网"),
        ("www.deepseek.com", "DeepSeek"),
        ("github.com", "GitHub"),
    ]
    
    all_ok = True
    for host, name in test_hosts:
        try:
            ip = socket.gethostbyname(host)
            print_result(True, f"{name} ({host}) -> {ip}")
        except socket.gaierror as e:
            print_result(False, f"{name} ({host}) - 解析失败: {e}")
            all_ok = False
        except Exception as e:
            print_result(False, f"{name} ({host}) - 错误: {e}")
            all_ok = False
    
    return all_ok


def check_http_connection():
    """检查 HTTP/HTTPS 连接"""
    print_section("HTTP/HTTPS 连接测试")
    
    test_urls = [
        ("http://www.baidu.com", "百度 (HTTP)"),
        ("https://www.baidu.com", "百度 (HTTPS)"),
        ("https://www.byd.com/cn", "比亚迪官网"),
        ("https://www.deepseek.com", "DeepSeek"),
    ]
    
    all_ok = True
    for url, name in test_urls:
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
                timeout=10
            )
            response = urllib.request.urlopen(req)
            status = response.getcode()
            print_result(True, f"{name}: HTTP {status}")
            response.close()
        except urllib.error.HTTPError as e:
            print_result(False, f"{name}: HTTP 错误 {e.code}")
            all_ok = False
        except urllib.error.URLError as e:
            print_result(False, f"{name}: 连接失败 - {e.reason}")
            all_ok = False
        except Exception as e:
            print_result(False, f"{name}: 错误 - {str(e)}")
            all_ok = False
    
    return all_ok


def check_requests_library():
    """使用 requests 库测试（Agent 实际使用的库）"""
    print_section("Requests 库测试")
    
    try:
        import requests
        
        test_urls = [
            ("https://www.baidu.com", "百度"),
            ("https://www.byd.com/cn", "比亚迪官网"),
        ]
        
        all_ok = True
        for url, name in test_urls:
            try:
                response = requests.get(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
                    timeout=10
                )
                if response.status_code == 200:
                    content_length = len(response.text)
                    print_result(True, f"{name}: HTTP {response.status_code}, 内容 {content_length} 字符")
                else:
                    print_result(False, f"{name}: HTTP {response.status_code}")
                    all_ok = False
            except requests.exceptions.ProxyError as e:
                print_result(False, f"{name}: 代理错误 - {e}")
                all_ok = False
            except requests.exceptions.SSLError as e:
                print_result(False, f"{name}: SSL 证书错误 - {e}")
                all_ok = False
            except requests.exceptions.ConnectionError as e:
                print_result(False, f"{name}: 连接错误 - {e}")
                all_ok = False
            except requests.exceptions.Timeout:
                print_result(False, f"{name}: 请求超时")
                all_ok = False
            except Exception as e:
                print_result(False, f"{name}: {type(e).__name__} - {e}")
                all_ok = False
        
        return all_ok
        
    except ImportError:
        print_result(False, "requests 库未安装")
        return False


def check_ssl_certificates():
    """检查 SSL 证书状态"""
    print_section("SSL 证书检查")
    
    test_hosts = [
        ("www.baidu.com", 443),
        ("www.byd.com", 443),
        ("github.com", 443),
    ]
    
    all_ok = True
    for host, port in test_hosts:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    print_result(True, f"{host}: SSL 正常, 加密: {cipher[0]}")
        except ssl.SSLError as e:
            print_result(False, f"{host}: SSL 错误 - {e}")
            all_ok = False
        except Exception as e:
            print_result(False, f"{host}: 连接失败 - {e}")
            all_ok = False
    
    return all_ok


def check_proxy_settings():
    """检查代理设置"""
    print_section("代理设置检查")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    has_proxy = False
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ⚠️  {var} = {value}")
            has_proxy = True
    
    if not has_proxy:
        print_result(True, "未检测到系统代理设置")
    else:
        print("\n  提示: 检测到代理设置，如果代理配置错误可能导致无法访问网页")
    
    # 检查 requests 的代理
    try:
        import requests
        proxies = requests.utils.get_environ_proxies("https://www.baidu.com")
        if proxies:
            print(f"  ⚠️  requests 检测到的代理: {proxies}")
        else:
            print_result(True, "requests 未使用代理")
    except:
        pass
    
    return True


def check_windows_specific():
    """检查 Windows 特定问题"""
    print_section("Windows 特定检查")
    
    # 检查 Windows 防火墙（简单检查）
    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "show", "currentprofile"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "State ON" in result.stdout:
            print_result(True, "Windows 防火墙: 已启用（正常）")
        elif "State OFF" in result.stdout:
            print_result(True, "Windows 防火墙: 已禁用")
        else:
            print_result(True, "Windows 防火墙: 状态未知")
    except Exception as e:
        print(f"  ⚠️  无法检查防火墙状态: {e}")
    
    # 检查 hosts 文件
    hosts_path = Path(r"C:\Windows\System32\drivers\etc\hosts")
    if hosts_path.exists():
        try:
            content = hosts_path.read_text(encoding='utf-8', errors='ignore')
            lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
            if lines:
                print(f"  ⚠️  hosts 文件有 {len(lines)} 条自定义条目，可能影响网络访问")
                for line in lines[:5]:  # 只显示前5条
                    print(f"      {line.strip()}")
                if len(lines) > 5:
                    print(f"      ... 还有 {len(lines)-5} 条")
            else:
                print_result(True, "hosts 文件: 无异常条目")
        except Exception as e:
            print(f"  ⚠️  无法读取 hosts 文件: {e}")
    
    return True


def test_agent_web_tool():
    """测试 Agent 的网页工具"""
    print_section("Agent 网页工具测试")
    
    try:
        # 尝试导入并测试
        sys.path.insert(0, str(Path(__file__).parent))
        from tools.web_tool import WebTool
        
        web_tool = WebTool()
        
        print("  测试访问 https://www.baidu.com ...")
        result = web_tool.fetch_url("https://www.baidu.com")
        
        if result.startswith("❌"):
            print_result(False, f"Agent 网页工具测试失败: {result}")
            return False
        else:
            content_length = len(result)
            print_result(True, f"Agent 网页工具正常，获取内容 {content_length} 字符")
            return True
            
    except ImportError as e:
        print_result(False, f"无法导入 Agent 网页工具: {e}")
        return False
    except Exception as e:
        print_result(False, f"Agent 网页工具测试失败: {e}")
        return False


def print_suggestions(results):
    """输出修复建议"""
    print_section("修复建议")
    
    if not results['dependencies']:
        print("\n1. 安装缺失的依赖包:")
        print(f"   {sys.executable} -m pip install requests beautifulsoup4")
    
    if not results['dns']:
        print("\n2. DNS 解析问题:")
        print("   - 检查网络连接是否正常")
        print("   - 尝试更换 DNS 服务器（如 8.8.8.8 或 114.114.114.114）")
        print("   - 检查 hosts 文件是否有错误条目")
    
    if not results['http']:
        print("\n3. HTTP 连接问题:")
        print("   - 检查是否能正常访问百度/其他网站")
        print("   - 检查是否有代理软件或 VPN 干扰")
        print("   - 检查 Windows 防火墙设置")
    
    if not results['ssl']:
        print("\n4. SSL 证书问题:")
        print("   - 检查系统时间是否正确（证书有效期依赖正确时间）")
        print("   - 尝试更新 Windows 根证书")
        print("   - 检查是否有中间人代理或安全软件拦截 HTTPS")
    
    if not results['requests']:
        print("\n5. Requests 库问题:")
        print("   - 重新安装 requests: pip install --upgrade requests")
        print("   - 检查是否有代理环境变量设置错误")
    
    print("\n6. 通用排查步骤:")
    print("   - 重启网络适配器")
    print("   - 暂时关闭防火墙/杀毒软件测试")
    print("   - 使用浏览器访问同一网站确认网络正常")
    print("   - 检查公司/学校网络是否有特殊限制")


def main():
    print("=" * 60)
    print("  Windows 网络诊断工具")
    print("  用于排查 AI Agent 网页访问问题")
    print("=" * 60)
    
    results = {
        'python': check_python_env(),
        'dependencies': check_dependencies(),
        'dns': check_dns_resolution(),
        'http': check_http_connection(),
        'ssl': check_ssl_certificates(),
        'proxy': check_proxy_settings(),
        'windows': check_windows_specific(),
        'requests': check_requests_library(),
        'agent': test_agent_web_tool(),
    }
    
    # 总结
    print_section("诊断总结")
    
    check_items = [
        ("Python 环境", results['python']),
        ("依赖包", results['dependencies']),
        ("DNS 解析", results['dns']),
        ("HTTP 连接", results['http']),
        ("SSL 证书", results['ssl']),
        ("代理设置", results['proxy']),
        ("Windows 设置", results['windows']),
        ("Requests 库", results['requests']),
        ("Agent 网页工具", results['agent']),
    ]
    
    for name, status in check_items:
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    
    all_ok = all(results.values())
    
    print("\n" + "=" * 60)
    if all_ok:
        print("  ✅ 所有检查通过，网络环境正常")
        print("=" * 60)
        return 0
    else:
        print("  ❌ 发现网络问题，请根据下方建议修复")
        print("=" * 60)
        print_suggestions(results)
        return 1


if __name__ == "__main__":
    sys.exit(main())

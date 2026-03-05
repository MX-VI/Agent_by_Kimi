#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度网络诊断脚本 - 针对 urllib vs requests 差异
"""

import sys
import os


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def test_urllib_detail():
    """详细测试 urllib 问题"""
    print_section("详细测试 urllib")
    
    import urllib.request
    import urllib.error
    import ssl
    
    url = "https://www.baidu.com"
    
    # 测试 1: 最基础的请求
    print("\n1. 基础 urllib 请求...")
    try:
        response = urllib.request.urlopen(url, timeout=10)
        print(f"   ✅ 成功: HTTP {response.getcode()}")
        response.close()
    except Exception as e:
        print(f"   ❌ 失败: {type(e).__name__}: {e}")
    
    # 测试 2: 带 User-Agent
    print("\n2. 带 User-Agent 的请求...")
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=10)
        print(f"   ✅ 成功: HTTP {response.getcode()}")
        response.close()
    except Exception as e:
        print(f"   ❌ 失败: {type(e).__name__}: {e}")
    
    # 测试 3: 禁用 SSL 验证
    print("\n3. 禁用 SSL 验证的请求...")
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"   ✅ 成功: HTTP {response.getcode()}")
        response.close()
    except Exception as e:
        print(f"   ❌ 失败: {type(e).__name__}: {e}")
    
    # 测试 4: 检查代理处理器
    print("\n4. 检查 urllib 代理设置...")
    proxy_handler = urllib.request.ProxyHandler()
    opener = urllib.request.build_opener(proxy_handler)
    print(f"   默认代理处理器: {proxy_handler}")
    
    # 打印环境变量
    print("\n5. 相关环境变量...")
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY']:
        value = os.environ.get(key)
        if value:
            print(f"   {key} = {value}")


def test_requests_detail():
    """详细测试 requests"""
    print_section("详细测试 requests")
    
    import requests
    
    url = "https://www.baidu.com"
    
    # 测试 1: 基础请求
    print("\n1. 基础 requests 请求...")
    try:
        response = requests.get(url, timeout=10)
        print(f"   ✅ 成功: HTTP {response.status_code}, 长度 {len(response.text)}")
    except Exception as e:
        print(f"   ❌ 失败: {type(e).__name__}: {e}")
    
    # 测试 2: 带 headers
    print("\n2. 带 headers 的请求...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   ✅ 成功: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 失败: {type(e).__name__}: {e}")
    
    # 测试 3: 查看会话设置
    print("\n3. requests 会话默认设置...")
    session = requests.Session()
    print(f"   默认 headers: {dict(session.headers)}")
    
    # 检查信任证书
    print(f"   证书验证: 默认启用")
    print(f"   已安装证书: {requests.certs.where()}")


def test_bypass_cert_verify():
    """测试证书验证问题"""
    print_section("SSL 证书深度检查")
    
    import requests
    import urllib.request
    import ssl
    
    url = "https://www.byd.com/cn"
    
    print("\n1. requests 默认验证...")
    try:
        response = requests.get(url, timeout=10)
        print(f"   ✅ 成功: HTTP {response.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL 错误: {e}")
        print("\n   尝试禁用证书验证...")
        try:
            response = requests.get(url, verify=False, timeout=10)
            print(f"   ✅ 禁用验证后成功: HTTP {response.status_code}")
            print("   ⚠️  警告: 禁用证书验证不安全，仅用于测试")
        except Exception as e2:
            print(f"   ❌ 仍失败: {e2}")
    except Exception as e:
        print(f"   ❌ 其他错误: {type(e).__name__}: {e}")
    
    print("\n2. urllib 证书检查...")
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10, context=ctx)
        print(f"   ✅ 成功")
        response.close()
    except urllib.error.URLError as e:
        print(f"   ❌ 失败: {e.reason}")


def test_actual_agent_usage():
    """测试 Agent 实际使用场景"""
    print_section("Agent 实际使用场景测试")
    
    sys.path.insert(0, str(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from tools.web_tool import WebTool
        web_tool = WebTool()
        
        test_urls = [
            "https://www.baidu.com",
            "https://www.byd.com/cn",
            "https://www.deepseek.com",
        ]
        
        for url in test_urls:
            print(f"\n测试: {url}")
            try:
                result = web_tool.fetch_url(url)
                if result.startswith("❌"):
                    print(f"   ❌ fetch_url 失败: {result}")
                else:
                    print(f"   ✅ fetch_url 成功: {len(result)} 字符")
                    
                    # 测试内容提取
                    content = web_tool.extract_content(result)
                    print(f"   提取内容: {len(content)} 字符")
                    
            except Exception as e:
                print(f"   ❌ 异常: {type(e).__name__}: {e}")
                
    except Exception as e:
        print(f"❌ 导入失败: {e}")


def check_windows_cert_store():
    """检查 Windows 证书存储"""
    print_section("Windows 证书存储检查")
    
    import ssl
    import certifi
    
    print(f"\nPython 使用的证书文件:")
    print(f"  {certifi.where()}")
    
    # 检查证书文件是否存在
    if os.path.exists(certifi.where()):
        print(f"  ✅ 证书文件存在")
    else:
        print(f"  ❌ 证书文件不存在!")
    
    # 检查 SSL 默认上下文
    print(f"\nSSL 默认设置:")
    ctx = ssl.create_default_context()
    print(f"  检查主机名: {ctx.check_hostname}")
    print(f"  验证模式: {ctx.verify_mode}")


def main():
    print("=" * 60)
    print("  深度网络诊断工具")
    print("  排查 urllib vs requests 差异")
    print("=" * 60)
    
    test_urllib_detail()
    test_requests_detail()
    test_bypass_cert_verify()
    check_windows_cert_store()
    test_actual_agent_usage()
    
    print_section("诊断完成")
    print("\n如果 urllib 失败但 requests 成功:")
    print("  → 这是正常现象，Agent 使用 requests 库")
    print("  → 你的 Agent 应该能正常访问网页")
    print("\n如果 Agent 仍无法访问网页:")
    print("  → 请检查 Agent 使用的具体 URL")
    print("  → 某些网站可能有反爬虫机制")
    print("  → 尝试更换 User-Agent 或添加延迟")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查脚本 - 用于 PyCharm
运行前检查 Python 环境和依赖
"""

import sys
import subprocess
import os
from pathlib import Path


def print_section(title):
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


def check_python():
    """检查 Python 版本和路径"""
    print_section("Python 环境")
    print(f"Python 版本: {sys.version}")
    print(f"Python 可执行文件: {sys.executable}")
    print(f"平台: {sys.platform}")
    
    # 检查版本是否 >= 3.8
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python 版本符合要求 (>= 3.8)")
    else:
        print(f"❌ Python 版本过低，需要 >= 3.8")
    
    return True


def check_pip():
    """检查 pip 是否可用"""
    print_section("Pip 环境")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Pip 可用")
        print(f"   {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Pip 检查失败: {e}")
        return False


def check_dependencies():
    """检查依赖包"""
    print_section("依赖检查")
    
    required_packages = [
        ("openai", "1.0.0"),
        ("requests", "2.31.0"),
        ("beautifulsoup4", "4.12.0"),
        ("markdown", "3.5.0"),
    ]
    
    all_ok = True
    
    print("\n【必需依赖】")
    for package, min_version in required_packages:
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            print(f"  ✅ {package:20s} {version}")
        except ImportError:
            print(f"  ❌ {package:20s} 未安装")
            all_ok = False
    
    return all_ok


def check_web_capability():
    """检查网页访问能力"""
    print_section("网页访问能力检查")
    
    web_ok = True
    
    # 1. 检查 requests（基础网页访问）
    try:
        import requests
        print(f"  ✅ requests 已安装 ({requests.__version__})")
        
        # 测试网络连接
        print(f"\n  测试网络连接...")
        try:
            response = requests.get("https://www.baidu.com", timeout=5)
            print(f"  ✅ 网络连接正常 (HTTP {response.status_code})")
        except Exception as e:
            print(f"  ⚠️  网络连接测试失败: {e}")
            print(f"      请检查网络设置或代理配置")
            web_ok = False
            
    except ImportError:
        print(f"  ❌ requests 未安装")
        print(f"      运行: {sys.executable} -m pip install requests")
        web_ok = False
    
    # 2. 检查 BeautifulSoup（HTML解析）
    try:
        from bs4 import BeautifulSoup
        print(f"  ✅ BeautifulSoup 已安装")
    except ImportError:
        print(f"  ❌ BeautifulSoup 未安装")
        print(f"      运行: {sys.executable} -m pip install beautifulsoup4")
        web_ok = False
    
    # 3. 检查 playwright（JS渲染，可选）
    print(f"\n【可选依赖 - JavaScript 渲染】")
    try:
        import playwright
        print(f"  ✅ Playwright 已安装")
        
        # 检查浏览器是否安装
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser_path = p.chromium.executable_path
                if browser_path and Path(browser_path).exists():
                    print(f"  ✅ Chromium 浏览器已安装")
                    print(f"      可以访问动态渲染的网站（Vue/React等）")
                else:
                    print(f"  ⚠️  Chromium 浏览器未安装")
                    print(f"      运行: {sys.executable} -m playwright install chromium")
        except Exception as e:
            print(f"  ⚠️  Playwright 初始化失败: {e}")
            print(f"      运行: {sys.executable} -m playwright install chromium")
            
    except ImportError:
        print(f"  ⚠️  Playwright 未安装")
        print(f"      静态网页可以访问，但动态网页（Vue/React）可能无法获取内容")
        print(f"      如需完整功能，运行: {sys.executable} -m pip install playwright")
        print(f"      然后: {sys.executable} -m playwright install chromium")
    
    return web_ok


def test_web_access():
    """实际测试网页访问"""
    print_section("网页访问测试")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        test_url = "https://www.byd.com/cn"
        print(f"  测试访问: {test_url}")
        
        try:
            response = requests.get(test_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            print(f"  ✅ 请求成功 (HTTP {response.status_code})")
            
            # 尝试解析
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "无标题"
            print(f"  📄 页面标题: {title[:50]}")
            
            # 检查内容长度
            text_content = soup.get_text(strip=True)
            if len(text_content) > 1000:
                print(f"  ✅ 成功获取页面内容 ({len(text_content)} 字符)")
            else:
                print(f"  ⚠️  页面内容较少 ({len(text_content)} 字符)")
                print(f"      可能是动态渲染网站，建议安装 Playwright")
                
        except Exception as e:
            print(f"  ❌ 访问失败: {e}")
            return False
            
    except ImportError as e:
        print(f"  ❌ 缺少必要依赖: {e}")
        return False
    
    return True


def check_project_files():
    """检查项目文件是否完整"""
    print_section("项目文件检查")
    
    required_files = [
        "main_tkinter.py",
        "agent.py",
        "config.py",
        "requirements_minimal.txt",
        "tools/__init__.py",
        "tools/file_tool.py",
        "tools/web_tool.py",
    ]
    
    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} 缺失")
            all_ok = False
    
    return all_ok


def check_api_key():
    """检查 API Key 配置"""
    print_section("API Key 检查")
    
    try:
        import config
        key = config.DEEPSEEK_API_KEY
        if key and key.startswith("sk-"):
            masked = key[:8] + "****" + key[-4:]
            print(f"  ✅ API Key 已配置: {masked}")
            return True
        else:
            print(f"  ⚠️  API Key 格式可能不正确")
            return False
    except Exception as e:
        print(f"  ❌ 无法读取配置: {e}")
        return False


def print_suggestions(deps_ok, web_ok):
    """提供修复建议"""
    print_section("修复建议")
    
    if not deps_ok:
        print("\n1. 安装缺失的依赖:")
        print(f"   {sys.executable} -m pip install -r requirements_minimal.txt")
    
    if not web_ok:
        print("\n2. 修复网页访问功能:")
        print(f"   a) 基础网页访问:")
        print(f"      {sys.executable} -m pip install requests beautifulsoup4")
        print(f"   b) 动态网页渲染（Vue/React网站）:")
        print(f"      {sys.executable} -m pip install playwright")
        print(f"      {sys.executable} -m playwright install chromium")
    
    print("\n3. 在 PyCharm 中设置解释器:")
    print("   File → Settings → Project → Python Interpreter")
    print(f"   选择: {sys.executable}")
    
    print("\n4. 如果网络连接失败:")
    print("   - 检查是否能正常访问百度/谷歌")
    print("   - 检查是否需要配置代理")
    print("   - 检查防火墙设置")


def main():
    print("=" * 50)
    print("  AI Agent 环境检查工具")
    print("=" * 50)
    
    checks = {
        "Python 环境": check_python(),
        "Pip 环境": check_pip(),
        "项目文件": check_project_files(),
        "API Key": check_api_key(),
    }
    
    deps_ok = check_dependencies()
    web_ok = check_web_capability()
    test_ok = test_web_access()
    
    # 总结
    print_section("检查总结")
    all_ok = all(checks.values()) and deps_ok and web_ok
    
    for name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"  {'✅' if deps_ok else '❌'} 依赖包")
    print(f"  {'✅' if web_ok else '❌'} 网页访问能力")
    print(f"  {'✅' if test_ok else '❌'} 网页访问测试")
    
    print("\n" + "=" * 50)
    if all_ok and test_ok:
        print("  ✅ 所有检查通过，可以运行 main_tkinter.py")
        print("=" * 50)
        return 0
    else:
        print("  ❌ 环境有问题，请根据上方提示修复")
        print("=" * 50)
        print_suggestions(deps_ok, web_ok)
        return 1


if __name__ == "__main__":
    sys.exit(main())

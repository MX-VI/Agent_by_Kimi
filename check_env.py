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
        ("gradio", "4.0.0"),
        ("markdown", "3.5.0"),
    ]
    
    optional_packages = [
        ("playwright", "1.40.0"),
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
    
    print("\n【可选依赖】")
    for package, min_version in optional_packages:
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            print(f"  ✅ {package:20s} {version}")
        except ImportError:
            print(f"  ⚠️  {package:20s} 未安装（网页访问功能受限）")
    
    return all_ok


def check_project_files():
    """检查项目文件是否完整"""
    print_section("项目文件检查")
    
    required_files = [
        "main.py",
        "agent.py",
        "config.py",
        "requirements.txt",
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


def suggest_fixes(missing_deps):
    """提供修复建议"""
    print_section("修复建议")
    
    print("\n1. 安装缺失的依赖:")
    print(f"   {sys.executable} -m pip install -r requirements.txt")
    
    print("\n2. 如果 greenlet/playwright 安装失败:")
    print("   - 方法一: 使用预编译版本")
    print(f"   {sys.executable} -m pip install --only-binary :all: -r requirements.txt")
    print("   - 方法二: 安装 Visual C++ Build Tools")
    print("   下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    
    print("\n3. 在 PyCharm 中设置解释器:")
    print("   File → Settings → Project → Python Interpreter")
    print(f"   选择: {sys.executable}")


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
    
    # 总结
    print_section("检查总结")
    all_ok = all(checks.values()) and deps_ok
    
    for name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"  {'✅' if deps_ok else '❌'} 依赖包")
    
    print("\n" + "=" * 50)
    if all_ok:
        print("  ✅ 所有检查通过，可以运行 main.py")
        print("=" * 50)
        return 0
    else:
        print("  ❌ 环境有问题，请根据上方提示修复")
        print("=" * 50)
        suggest_fixes([])
        return 1


if __name__ == "__main__":
    sys.exit(main())

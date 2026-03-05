@echo off
chcp 65001 >nul
echo =========================================
echo    修复 greenlet 安装失败
echo =========================================
echo.
echo 方案：使用预编译版本，无需安装编译器
echo.

set PYTHON=J:\PYTHON\python.exe

echo 【1】升级 pip 和 setuptools...
%PYTHON% -m pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

echo 【2】安装预编译的 greenlet...
%PYTHON% -m pip install greenlet --only-binary :all: -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

echo 【3】安装其他依赖（跳过编译）...
%PYTHON% -m pip install openai requests beautifulsoup4 markdown gradio -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

echo 【4】单独安装 playwright（可能需要单独处理）...
%PYTHON% -m pip install playwright --only-binary :all: -i https://pypi.tuna.tsinghua.edu.cn/simple 2>nul
if errorlevel 1 (
    echo ⚠️ playwright 安装失败，可能需要安装 Visual C++ Build Tools
    echo    或者暂时跳过 playwright（网页功能会受限）
)
echo.

echo 【5】验证安装...
%PYTHON% -c "import gradio; print('✅ gradio 版本:', gradio.__version__)" 2>nul || echo ❌ gradio 导入失败
%PYTHON% -c "import openai; print('✅ openai 版本:', openai.__version__)" 2>nul || echo ❌ openai 导入失败
echo.

echo =========================================
echo 如果仍有错误，运行 fix_greenlet_advanced.bat
echo =========================================
pause

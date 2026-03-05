@echo off
chcp 65001 >nul
echo =========================================
echo    Python 环境诊断工具
echo =========================================
echo.

echo 【1】检查 Python 路径...
where python 2>nul && python --version
if errorlevel 1 (
    echo ❌ 未找到 python 命令，尝试 python3...
    where python3 2>nul && python3 --version
)
echo.

echo 【2】检查 pip 路径...
where pip 2>nul && pip --version
if errorlevel 1 (
    echo ❌ 未找到 pip 命令，尝试 pip3...
    where pip3 2>nul && pip3 --version
)
echo.

echo 【3】检查 Python 可执行文件位置...
python -c "import sys; print('可执行文件:', sys.executable)" 2>nul || python3 -c "import sys; print('可执行文件:', sys.executable)" 2>nul
echo.

echo 【4】检查 pip 安装位置...
pip show pip 2>nul | findstr "Location" || pip3 show pip 2>nul | findstr "Location"
echo.

echo 【5】尝试导入 gradio...
python -c "import gradio; print('✅ Gradio 版本:', gradio.__version__)" 2>nul || python3 -c "import gradio; print('✅ Gradio 版本:', gradio.__version__)" 2>nul || echo ❌ 无法导入 gradio
echo.

echo 【6】检查 site-packages 路径...
python -c "import site; print('\\n'.join(site.getsitepackages()))" 2>nul || python3 -c "import site; print('\\n'.join(site.getsitepackages()))" 2>nul
echo.

echo =========================================
echo 诊断完成！
echo =========================================
pause

@echo off
chcp 65098 >nul
echo =========================================
echo    高级修复：安装 Visual Studio 编译器
echo =========================================
echo.

echo 【方法1】自动下载安装 Build Tools（推荐）
echo 正在下载 Visual Studio Build Tools...
echo.

# 下载 vs_buildtools.exe
curl -L -o %TEMP%\vs_buildtools.exe "https://aka.ms/vs/17/release/vs_buildtools.exe"

echo 安装 C++ 编译工具...
%TEMP%\vs_buildtools.exe --quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended

echo.
echo 安装完成后，重新运行：
echo    J:\PYTHON\python.exe -m pip install -r requirements.txt

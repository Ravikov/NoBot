@echo off
chcp 65001 > nul
title NoBot 轻量的ai聊天机器人
echo ======================================
echo      NoBot 一键启动脚本
echo ======================================
echo.

:: 检查虚拟环境
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境，请先运行 python -m venv .venv
    echo        然后执行 pip install -r requirements.txt
    pause
    exit /b 1
)

:: 显示Python版本
echo 使用Python:
.venv\Scripts\python --version

:: 启动主程序（前台运行）
echo.
echo 正在启动 NoBot...
echo 程序运行中可随时按 Ctrl+C 退出。
echo.
.venv\Scripts\python -u main.py

:: 程序退出后的提示
echo.
echo NoBot 程序已退出。
pause

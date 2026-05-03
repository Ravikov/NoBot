@echo off
chcp 65001 > nul
title NoBot 轻量的ai聊天机器人
echo ======================================
echo      NoBot Windows一键启动脚本
echo ======================================
echo.

:: 检查Python环境
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请确认已安装并配置环境变量。
    pause
    exit /b 1
)

:: 显示当前Python路径和版本
echo 使用Python: 
python --version

:: 启动主程序
echo.
echo 正在启动 NoBot...
echo 程序运行中可随时按 Ctrl+C 退出。
echo.
python -u main.py

:: 程序退出后的提示
echo.
echo NoBot 程序已退出。
pause
#!/usr/bin/env bash
set -e

echo "======================================"
echo "      NoBot 轻量的ai聊天机器人"
echo "======================================"
echo ""

# 检查虚拟环境
if [ ! -f ".venv/bin/python" ]; then
    echo "[错误] 未找到虚拟环境，请先运行 python3 -m venv .venv"
    echo "       然后执行 pip install -r requirements.txt"
    exit 1
fi

# 显示Python版本
echo "使用Python:"
.venv/bin/python --version

# 启动主程序（前台运行）
echo ""
echo "正在启动 NoBot..."
echo "程序运行中可随时按 Ctrl+C 退出。"
echo ""
.venv/bin/python -u main.py

# 程序退出后的提示
echo ""
echo "NoBot 程序已退出。"

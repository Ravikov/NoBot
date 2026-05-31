# NoBot

📖 简体中文 | [English](./README.md)

## 一个轻量的简易AI聊天机器人

本项目基于 Python 开发，利用 `requests` 库调用 API 接口而非使用 OpenAI 的 SDK。

这是我第一个正式的编程项目，边学边写。如果有些地方做得不够好，恳请您不要介意。如果能有人指点一二，感激不尽！

## 快速开始

**请确保已安装 Python 3.10 或更高版本。**

```bash
git clone https://github.com/Ravikov/NoBot.git
cd NoBot
python -m venv .venv          # 创建虚拟环境（推荐）
.venv\Scripts\pip install -r requirements.txt   # Windows
# 或
.venv/bin/pip install -r requirements.txt       # Linux/macOS
python main.py
```

首次启动会自动进入配置引导，按提示输入各模型的 URL、API Key 和模型名称即可。

### 快速启动脚本

- **Windows:** 双击 `Run.bat`
- **Linux/macOS:** 终端运行 `./Run.sh`

### 配置说明

- 主模型、辅助模型、联网搜索模型、多模态理解模型均需配置
- 角色提示词请写入 `nobot/config/soul.md`
- 如果配置出现错误，可删除 `nobot/config/config.json` 后重新运行，程序会自动重建默认配置

## 启动方式

程序启动后选择对应编号：

| 编号 | 模式 | 说明 |
|---|---|---|
| 1 | Webhook | Flask 服务，用于对接第三方平台 |
| 2 | 命令行 | 直接在终端输入问题 |
| 3 | 微信个人号 | 暂不可用 |
| 4 | 微信 ClawBot | ✅ 推荐，扫描二维码登录后自动收发消息 |
| set | 配置引导 | 重新配置模型参数 |
| save/load | 备份/恢复 | 备份或恢复配置文件 |
| del | 清理日志 | 删除 `debug/bot.log` |

## 项目结构

```
NoBot/
├── main.py                     # 程序入口
├── Run.bat / Run.sh            # 快速启动脚本
├── requirements.txt            # Python 依赖
│
├── message/                    # 消息协议层
│   ├── msg.py                  # 基类 Message, ReplyIn, ReplyOut
│   └── clawbot/
│       └── wechatmsg.py        # WechatBotMessage 基类（继承 Message）
│
├── IMchat/                     # 微信 ClawBot 实现
│   ├── clawbot/
│   │   ├── wechat_clawbot.py   # 主控：登录、token校验、主循环
│   │   ├── wechat_common.py    # 工具函数：配置读写、请求头、UIN
│   │   ├── getmsg/             # 消息接收模块
│   │   │   ├── getupdate.py    #   长轮询 API
│   │   │   ├── handlemsg.py    #   消息路由与内容提取
│   │   │   ├── mediagetter.py  #   多媒体下载与 AES 解密
│   │   │   ├── waitimer.py     #   智能等待决策
│   │   │   └── replymsg.py     #   调用回复引擎
│   │   └── sendmsg/            # 消息发送模块
│   │       ├── send.py         #   发送消息（分条发送）
│   │       └── sendtyping.py   #   打字状态指示
│   └── etc/
│       └── start_ways.py       # 其他启动方式（webhook 等）
│
├── nobot/                      # 核心逻辑
│   ├── common.py               # 全局配置路径、记忆读写
│   ├── guide.py                # 命令行配置向导
│   ├── config/                 # 配置文件目录
│   │   ├── config.json         # API 配置
│   │   ├── config.json.bak     # 备份
│   │   ├── soul.md             # 角色提示词
│   │   └── wechat_clawbot.json # 微信登录信息（自动生成）
│   ├── memory/
│   │   └── memory.json         # 对话历史与记忆
│   └── src/
│       └── core/
│           ├── get_reply/
│           │   ├── reply.py    # ReplyHandler: 消息路由与回复生成
│           │   └── touch_llm.py # API 调用底层
│           └── mem/
│               └── memory.py   # 记忆总结压缩
│
├── debug/                      # 调试与日志
│   ├── bot.log                 # 运行日志
│   ├── states.json             # token 用量统计
│   └── response.json           # 最近一次 API 原始响应
│
└── check.py                    # 启动前完整性检查
```

## 快捷指令

在聊天中直接发送：

- `/rememory` — 清除机器人记忆
- `/memory` — 主动触发记忆总结

## 已支持功能

- ✅ 文本消息收发
- ✅ 图片消息接收 + AI 多模态理解
- ✅ 视频消息接收（实验性）
- ✅ 多条消息积累 + 智能等待
- ✅ 长轮询实时接收
- ✅ QR 码扫码登录
- ❌ 图片/视频发送 — 待 ilink 协议确认后实现

## 结语

这是我第一个正式项目。如果你有建议或发现了 bug，欢迎提 Issue，感激不尽！

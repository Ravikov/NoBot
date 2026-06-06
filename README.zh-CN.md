# NoBot

📖 简体中文 | [English](./README.md)

一个轻量的 AI 微信聊天机器人（基于 ClawBot 接口）。

> 这是我的第一个正式编程项目，边学边写。如有不足请多包涵，若能指点一二，感激不尽！

---

## 快速开始

**Python ≥ 3.10**

```bash
git clone https://github.com/Ravikov/NoBot.git
cd NoBot
python -m venv .venv

# Windows:
.venv\Scripts\pip install -r requirements.txt
# Linux / macOS:
.venv/bin/pip install -r requirements.txt

python main.py
```

首次启动会自动进入配置引导，按提示填写各模型的 URL、API Key 和模型名称即可。

### 快速启动脚本

| 平台 | 方式 |
|---|---|
| Windows | 双击 `Run.bat` |
| Linux / macOS | 终端运行 `./Run.sh` |

### 配置说明

- 主模型、辅助模型、联网搜索模型、多模态理解模型均需配置
- 角色提示词写入 `nobot/config/soul.md`
- 如果配置出错，删除 `nobot/config/config.json` 后重跑，程序会自动重建默认配置

---

## 启动方式

程序启动后选择对应编号：

| 编号 | 模式 | 说明 |
|---|---|---|
| 1 | Webhook | Flask 服务，用于对接第三方平台 |
| 2 | 命令行 | 直接在终端输入问题 |
| 3 | 微信个人号 | ⏳ 暂不可用 |
| **4** | **微信 ClawBot** | ✅ **推荐** — 扫码登录后自动收发 |
| `set` | 配置引导 | 重新配置模型参数 |
| `save` / `load` | 备份 / 恢复 | 备份或恢复配置文件 |
| `del` | 清理日志 | 删除 `debug/bot.log` |

---

## 项目结构

```
NoBot/
├── main.py                        # 程序入口
├── Run.bat / Run.sh               # 快速启动脚本
├── requirements.txt               # Python 依赖
├── check.py                       # 启动前完整性检查
│
├── message/                       # 消息协议层
│   ├── msg.py                     # 基类：Message, ReplyIn, ReplyOut
│   └── clawbot/
│       └── clawbotmsg.py          # WechatBotMessage 基类
│
├── IMchat/                        # 微信 ClawBot 实现
│   └── clawbot/
│       ├── clawbot.py             # 主控：登录 / token 校验 / 主循环
│       ├── clawbot_common.py      # 工具函数：配置、请求头、UIN
│       ├── login.py               # ClawBot 登录（获取二维码、轮询扫码状态）
│       ├── config/
│       │   └── clawbot.json       # 微信登录态缓存（自动生成）
│       ├── debug/
│       │   └── request.json       # 最近一次 API 请求记录
│       ├── getmsg/                # 消息接收
│       │   ├── getupdate.py       # 长轮询 API
│       │   ├── handlemsg.py       # 消息路由与内容提取
│       │   ├── mediagetter.py     # 多媒体下载与 AES 解密
│       │   ├── waitimer.py        # 智能等待决策
│       │   └── replymsg.py        # 调用回复引擎
│       └── sendmsg/               # 消息发送
│           ├── send.py            # 分条发送消息
│           └── sendtyping.py      # 打字状态指示
│
├── nobot/                         # 核心逻辑
│   └── src/
│       ├── common.py              # 全局配置路径、记忆读写
│       ├── guide.py               # 命令行配置向导
│       └── core/
│           ├── get_reply/
│           │   ├── reply.py       # ReplyHandler：消息路由与回复生成
│           │   └── touch_llm.py   # 底层 API 调用
│           └── mem/
│               └── memory.py      # 记忆压缩与摘要
│
├── nobot/config/                  # 配置文件目录
│   ├── config.json                # API 配置（URL / Key / 模型名）
│   ├── config.json.bak            # 备份
│   ├── soul.md                    # 角色提示词（system prompt）
│   └── wechat_clawbot.json        # 微信登录信息（自动生成）
│
├── nobot/memory/
│   ├── memory.json                # 对话历史与记忆
│   └── longhistory.json           # 长期记忆归档
│
├── debug/                         # 调试与日志
│   ├── log.py                     # 日志工具函数
│   ├── bot.log                    # 运行日志
│   ├── states.json                # Token 用量统计
│   └── response.json              # 最近一次 API 原始响应
│
└── etc/
    └── start_ways.py              # 各启动方式的入口分发
```

---

## 快捷指令

在聊天中直接发送：

| 指令 | 作用 |
|---|---|
| `/rememory` | 清除机器人记忆 |
| `/memory` | 主动触发记忆总结 |

---

## 功能状态

| 功能 | 状态 | 备注 |
|---|---|---|
| 文本消息收发 | ✅ | 已支持 |
| 图片消息接收 + AI 多模态理解 | ✅ | 已支持 |
| 视频消息接收 | 🧪 | 实验性 |
| 多条消息积累 + 智能等待 | ✅ | 已支持 |
| 长轮询实时接收 | ✅ | 已支持 |
| QR 码扫码登录 | ✅ | 已支持 |
| 图片 / 视频发送 | ❌ | 待 iLink 上传协议确认后实现 |

---

## 注意事项

- `debug/bot.log` 记录所有终端输出，请定期清理避免磁盘膨胀
- 角色提示词（system prompt）编辑 `nobot/config/soul.md`
- 配置文件坏了直接删掉，下次启动会自动生成默认配置
- 遇到问题欢迎提 [Issue](https://github.com/Ravikov/NoBot/issues) 🎉

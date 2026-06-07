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

首次启动会自动进入配置引导，按提示填写各模型的 URL、API Key 和模型名称即可，配置保存到 `nobot/config/<用户名>/config.json`。

### 快速启动脚本

| 平台 | 方式 |
|---|---|
| Windows | 双击 `Run.bat` |
| Linux / macOS | 终端运行 `./Run.sh` |

---

## 多用户系统

NoBot 支持多用户独立运行。每个用户拥有自己独立的：
- **API 配置**（`nobot/config/<用户名>/`）
- **记忆与对话历史**（`nobot/memory/<用户名>/`）
- **ClawBot 登录态**（`IMchat/clawbot/config/<用户名>/`）

启动时可以选择已有用户、创建新用户或删除用户（`main` 用户不可删除）。`main` 用户在首次启动时自动创建。

```
当前有如下用户:
名称: main,创建时间: 2026-06-07 13:31
请输入启动用户的名称,或输入delete来删除一个用户,输入creat来创建一个用户
>>>
```

非 `main` 用户首次启动时，可以选择沿用 `main` 用户的 API 配置作为起点。

---

## 启动方式

程序启动后选择对应编号：

| 编号 | 模式 | 说明 |
|---|---|---|
| 1 | Webhook | Flask 服务（`:5000`），用于对接第三方平台 |
| 2 | 命令行 | 直接在终端输入问题 |
| 3 | 微信个人号 | ⏳ 暂不可用 |
| **4** | **微信 ClawBot** | ✅ **推荐** — 扫码登录后自动收发消息 |
| **5** | **WebSocket** | ✅ WebSocket 服务端（`ws://127.0.0.1:7323`），供自定义客户端接入 |
| `set` | 配置引导 | 重新配置模型参数 |
| `save` / `load` | 备份 / 恢复 | 备份或恢复当前用户的配置文件 |
| `del` | 清理日志 | 删除 `debug/bot.log` |

### 模式说明

**Webhook (1)** — 启动 Flask 服务监听 5000 端口。向 `/webhook` 发送 POST 请求（JSON 格式，需含 `post_type: 'message'` 和消息文本），返回回复内容。

**命令行 (2)** — 交互式终端会话。输入问题即可获得回答，`Ctrl+C` 退出。

**微信 ClawBot (4)** — 通过 iLink 协议扫码登录微信，自动接收并回复消息。支持文本、图片、视频。

**WebSocket (5)** — 启动 WebSocket 服务端监听 `ws://127.0.0.1:7323`。收到消息后调用 LLM 生成回复并返回。如果 7323 端口被占用，会自动递增直到找到可用端口。

---

## 快捷指令

在聊天中直接发送（命令行模式同样适用）：

| 指令 | 作用 |
|---|---|
| `/rememory` | 清除当前用户的对话记忆 |
| `/memory` | 主动触发记忆总结 |
| `/rehistory` | 清除长上下文归档 |

---

## 功能状态

| 功能 | 状态 | 备注 |
|---|---|---|
| 文本消息收发 | ✅ | 已支持 |
| 图片接收 + AI 多模态理解 (type 2) | ✅ | 自动下载、AES 解密，由多模态模型描述 |
| 视频接收 (type 5) | 🧪 | 实验性 — 下载后提取描述 |
| 多条消息积累后统一处理 (type 9) | ✅ | 多条消息合并后再调用 LLM |
| 智能等待（LLM 决策） | ✅ | 辅助模型动态预测最优等待时间 |
| 长轮询实时接收 | ✅ | 已支持 |
| QR 码扫码登录 | ✅ | 已支持 |
| 智能联网搜索决策 | ✅ | 辅助模型判断是否需要联网搜索 |
| 多用户支持 | ✅ | 独立配置、记忆、ClawBot 登录态 |
| 时间注入 | ✅ | 可选将当前时间注入 LLM 上下文 |
| 复读鸡模式 | ✅ | 开启后原样回复消息（配置项 `repeat`） |
| 图片 / 视频发送 | ❌ | 待 iLink 上传协议确认后实现 |
| 微信个人号 (itchat) | ❌ | 已废弃，不可用 |

---

## 配置说明

### 配置引导（`set`）

交互式配置所有 API 端点与模型参数：

1. **是否启用联网搜索** — 开关 `or_search`
2. **各模型 API 信息**：
   - **主模型**（`API`）— 用于回复生成的 LLM
   - **辅助模型**（`secAPI`）— 用于搜索决策与智能等待
   - **联网搜索模型**（`searchAPI`）— 带搜索能力的 LLM
   - **多模态理解模型**（`multimodalAPI`）— 图片/视频理解
   - （生图模型已预留，暂未启用）
3. **主模型参数**：
   - `temperature`（0~2，默认 1.0）
   - `max_history_turns`（默认 20）— 达到此轮数后触发记忆压缩
   - `or_time_feel` — 是否将当前时间注入 LLM 上下文

### 核心配置项（`config/<用户名>/config.json`）

| 字段 | 默认值 | 说明 |
|---|---|---|
| `API` / `secAPI` / `searchAPI` / `multimodalAPI` / `imageAPI` | — | 各模型配置：`url`、`key`、`name` |
| `max_tokens` | 1500 | 最大生成 Token 数 |
| `temperature` | 1.0 | LLM 温度参数 |
| `prompt_file` | `"soul"` | 角色提示词文件名（自动补 `.md`） |
| `max_history_turns` | 20 | 触发记忆压缩的对话轮数 |
| `wait` | 8 | 消息积累基础等待时间（秒） |
| `llm_decide_wait` | true | 使用辅助模型动态调整等待时间 |
| `or_search` | true | 启用联网搜索 |
| `or_time_feel` | true | 注入当前时间到上下文 |
| `wash_comma` | false | 将中文逗号替换为空格 |
| `repeat` | false | 复读鸡模式 |
| `debug` | false | 在回复尾部追加缓存命中率 |
| `txt_wash` | `["*", "\\n", "。"]` | 从回复中剔除的字符列表 |

### 角色提示词

编辑 `nobot/config/<用户名>/soul.md`（或 `prompt_file` 指定的文件）来自定义机器人的角色性格（system prompt）。

---

## 项目结构

```
NoBot/
├── main.py                              # 程序入口
├── Run.bat / Run.sh                     # 快速启动脚本
├── requirements.txt                     # Python 依赖
├── check.py                             # 启动前完整性检查
│
├── message/                             # 消息协议层
│   ├── msg.py                           # 基类：Message, ReplyIn, ReplyOut
│   └── clawbot/
│       └── clawbotmsg.py                # WechatBotMessage 基类
│
├── IMchat/                              # 微信 ClawBot 实现
│   └── clawbot/
│       ├── clawbot.py                   # 主控：登录 / token 校验 / 主循环
│       ├── clawbot_common.py            # 工具函数：配置、请求头、UIN
│       ├── login.py                     # ClawBot 登录（获取二维码、轮询扫码状态）
│       ├── config/<用户名>/             # 各用户 ClawBot 登录态缓存（自动生成）
│       │   └── clawbot.json
│       ├── debug/
│       │   └── request.json             # 最近一次 API 请求记录
│       ├── getmsg/                      # 消息接收
│       │   ├── getupdate.py             # 长轮询 API
│       │   ├── handlemsg.py             # 消息路由与内容提取
│       │   ├── mediagetter.py           # 多媒体下载与 AES 解密
│       │   ├── waitimer.py              # 智能等待决策（由 LLM 驱动）
│       │   └── replymsg.py              # 调用回复引擎
│       └── sendmsg/                     # 消息发送
│           ├── send.py                  # 分条发送消息
│           └── sendtyping.py            # 打字状态指示
│
├── nobot/                               # 核心逻辑
│   └── src/
│       ├── common.py                    # 全局路径、配置读写、默认值
│       ├── guide.py                     # 命令行配置向导
│       ├── core/
│       │   ├── get_reply/
│       │   │   ├── reply.py             # ReplyHandler：消息路由与回复生成
│       │   │   └── touch_llm.py         # 底层 API 调用（文本 / 多模态 / 联网搜索）
│       │   └── mem/
│       │       └── memory.py            # 记忆压缩与摘要
│       └── user/
│           ├── user.py                  # 多用户系统：选择、创建、删除
│           └── userlist.json            # 用户注册表
│
├── nobot/config/<用户名>/               # 各用户的 API 配置
│   ├── config.json                      # API 配置（URL / Key / 模型名）
│   ├── config.json.bak                  # 备份
│   └── soul.md                          # 角色提示词（system prompt）
│
├── nobot/memory/<用户名>/
│   ├── memory.json                      # 对话历史与记忆
│   └── longhistory.json                 # 长期记忆归档
│
├── websocket/
│   └── server.py                        # WebSocket 服务端（模式 5）
│
├── debug/                               # 调试与日志
│   ├── log.py                           # 日志工具函数
│   ├── bot.log                          # 运行日志
│   ├── states.json                      # Token 用量统计
│   └── response.json                    # 最近一次 API 原始响应
│
└── etc/
    └── start_ways.py                    # 各启动方式的入口分发
```

---

## 注意事项

- `debug/bot.log` 记录所有终端输出，可在启动菜单用 `del` 命令定期清理，避免磁盘膨胀
- 角色提示词（system prompt）编辑 `nobot/config/<用户名>/soul.md`
- 配置文件坏了直接删掉，下次启动会自动生成默认配置
- 不支持的微信消息类型会记录日志并原样返回
- 遇到问题欢迎提 [Issue](https://github.com/Ravikov/NoBot/issues) 🎉

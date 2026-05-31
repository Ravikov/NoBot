# NoBot

📖 English | [简体中文](./README.zh-CN.md)

A lightweight AI chatbot for WeChat (ClawBot interface).

> This README was translated from Chinese. If there are inaccuracies, please refer to the Chinese version (`README.zh-CN.md`).

## Quick Start

**Python 3.10+ required.**

```bash
git clone https://github.com/Ravikov/NoBot.git
cd NoBot
python -m venv .venv
# Windows:
.venv\Scripts\pip install -r requirements.txt
# Linux/macOS:
.venv/bin/pip install -r requirements.txt
python main.py
```

On first launch, the program will guide you through configuration (API keys, model names, etc.).

### Quick Start Scripts

- **Windows:** Double-click `Run.bat`
- **Linux/macOS:** Run `./Run.sh`

## Project Structure

```
NoBot/
├── main.py                     # Entry point
├── Run.bat / Run.sh            # Quick launchers
├── requirements.txt
│
├── message/                    # Message protocol layer
│   ├── msg.py                  # Base: Message, ReplyIn, ReplyOut
│   └── clawbot/
│       └── wechatmsg.py        # WechatBotMessage base class
│
├── IMchat/                     # WeChat ClawBot implementation
│   ├── clawbot/
│   │   ├── wechat_clawbot.py   # Main controller: login, token, main loop
│   │   ├── wechat_common.py    # Utilities: config, headers, UIN
│   │   ├── getmsg/             # Message receiving
│   │   │   ├── getupdate.py    #   Long-polling API
│   │   │   ├── handlemsg.py    #   Message routing & content extraction
│   │   │   ├── mediagetter.py  #   Media download & AES decryption
│   │   │   ├── waitimer.py     #   Smart wait decision
│   │   │   └── replymsg.py     #   Reply engine bridge
│   │   └── sendmsg/            # Message sending
│   │       ├── send.py         #   Split-message sending
│   │       └── sendtyping.py   #   Typing indicator
│   └── etc/
│       └── start_ways.py       # Other launch modes
│
├── nobot/                      # Core logic
│   ├── common.py               # Paths, config loading, history I/O
│   ├── guide.py                # CLI configuration wizard
│   ├── config/                 # Config files
│   │   ├── config.json         # API keys & model settings
│   │   ├── config.json.bak     # Backup
│   │   ├── soul.md             # System prompt
│   │   └── wechat_clawbot.json # WeChat credentials (auto-generated)
│   ├── memory/
│   │   └── memory.json         # Conversation history & memory
│   └── src/core/
│       ├── get_reply/
│       │   ├── reply.py        # ReplyHandler: message routing & reply generation
│       │   └── touch_llm.py    # Low-level API calls
│       └── mem/
│           └── memory.py       # Memory compression & summarization
│
├── debug/                      # Debug & logs
│   ├── bot.log                 # Runtime log
│   ├── states.json             # Token usage stats
│   └── response.json           # Latest API raw response
│
└── check.py                    # Pre-launch integrity check
```

## Launch Modes

Select by number on startup:

| Mode | Description |
|---|---|
| 1 — Webhook | Flask server, for third-party integration |
| 2 — CLI | Type questions directly in terminal |
| 3 — WeChat Personal | Currently unavailable |
| **4 — WeChat ClawBot** | ✅ Recommended — scan QR code to login |
| set | Re-run configuration wizard |
| save / load | Backup / restore config |
| del | Clean log file |

## Quick Commands

Send these in chat:

- `/rememory` — Clear bot's memory
- `/memory` — Trigger memory summarization

## Features

- ✅ Text message send & receive
- ✅ Image message receive + AI multimodal understanding
- ✅ Video message receive (experimental)
- ✅ Multi-message buffering with smart wait
- ✅ Long-polling real-time message fetch
- ✅ QR code scan login
- ❌ Image/video sending — pending iLink upload protocol

## Notes

- `debug/bot.log` stores all terminal output. Clean it periodically to avoid disk bloat.
- The system prompt goes in `nobot/config/soul.md`.
- If you break a config file, just delete it — the program recreates defaults on next launch.

## Final Words

This is my first real project, built while learning Python. If you find bugs or have suggestions, issues are very welcome!

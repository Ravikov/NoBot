# NoBot

📖 English | [简体中文](./README.zh-CN.md)

A lightweight AI chatbot for WeChat, built on the ClawBot interface.

> This is my first real project, built while learning Python. If something could be better, please bear with me — and if you have advice, I'd be truly grateful!

---

## Quick Start

**Requires Python ≥ 3.10**

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

On first launch, the configuration wizard will walk you through setting up API URLs, keys, and model names.

### Quick Launch Scripts

| Platform | How |
|---|---|
| Windows | Double-click `Run.bat` |
| Linux / macOS | Run `./Run.sh` in terminal |

### Configuration Notes

- Main model, auxiliary model, web-search model, and multimodal model all need to be configured
- System prompt goes in `nobot/config/soul.md`
- If you break a config file, just delete it — the program regenerates defaults on next launch

---

## Launch Modes

Select by number at startup:

| # | Mode | Description |
|---|---|---|
| 1 | Webhook | Flask server for third-party integration |
| 2 | CLI | Type questions directly in the terminal |
| 3 | Personal WeChat | ⏳ Unavailable for now |
| **4** | **WeChat ClawBot** | ✅ **Recommended** — scan QR code, auto send & receive |
| `set` | Config Wizard | Re-run the configuration guide |
| `save` / `load` | Backup / Restore | Backup or restore config files |
| `del` | Clean logs | Delete `debug/bot.log` |

---

## Project Structure

```
NoBot/
├── main.py                        # Entry point
├── Run.bat / Run.sh               # Quick launcher scripts
├── requirements.txt               # Python dependencies
├── check.py                       # Pre-launch integrity check
│
├── message/                       # Message protocol layer
│   ├── msg.py                     # Base classes: Message, ReplyIn, ReplyOut
│   └── clawbot/
│       └── clawbotmsg.py          # WechatBotMessage base class
│
├── IMchat/                        # WeChat ClawBot implementation
│   └── clawbot/
│       ├── clawbot.py             # Main controller: login, token, main loop
│       ├── clawbot_common.py      # Utilities: config, headers, UIN
│       ├── login.py               # ClawBot login (QR fetch, scan polling)
│       ├── config/
│       │   └── clawbot.json       # WeChat session cache (auto-generated)
│       ├── debug/
│       │   └── request.json       # Latest API request dump
│       ├── getmsg/                # Message receiving
│       │   ├── getupdate.py       # Long-polling API
│       │   ├── handlemsg.py       # Message routing & content extraction
│       │   ├── mediagetter.py     # Media download & AES decryption
│       │   ├── waitimer.py        # Smart wait decision
│       │   └── replymsg.py        # Reply engine bridge
│       └── sendmsg/               # Message sending
│           ├── send.py            # Split-message sending
│           └── sendtyping.py      # Typing indicator
│
├── nobot/                         # Core logic
│   └── src/
│       ├── common.py              # Paths, config loading, history I/O
│       ├── guide.py               # CLI configuration wizard
│       └── core/
│           ├── get_reply/
│           │   ├── reply.py       # ReplyHandler: routing & reply generation
│           │   └── touch_llm.py   # Low-level API calls
│           └── mem/
│               └── memory.py      # Memory compression & summarization
│
├── nobot/config/                  # Configuration files
│   ├── config.json                # API config (URL / Key / model name)
│   ├── config.json.bak            # Backup
│   ├── soul.md                    # System prompt (bot personality)
│   └── wechat_clawbot.json        # WeChat session data (auto-generated)
│
├── nobot/memory/
│   ├── memory.json                # Conversation history & memory
│   └── longhistory.json           # Long-term memory archive
│
├── debug/                         # Debug & logs
│   ├── log.py                     # Logging utility
│   ├── bot.log                    # Runtime log
│   ├── states.json                # Token usage stats
│   └── response.json              # Latest raw API response
│
└── etc/
    └── start_ways.py              # Launch mode dispatcher
```

---

## Quick Commands

Send these in chat:

| Command | Effect |
|---|---|
| `/rememory` | Clear bot memory |
| `/memory` | Trigger memory summarization |

---

## Feature Status

| Feature | Status | Notes |
|---|---|---|
| Text message send & receive | ✅ | Done |
| Image receive + AI multimodal | ✅ | Done |
| Video receive | 🧪 | Experimental |
| Multi-message buffering + smart wait | ✅ | Done |
| Long-polling real-time fetch | ✅ | Done |
| QR code scan login | ✅ | Done |
| Image / video sending | ❌ | Pending iLink upload protocol |

---

## Notes

- `debug/bot.log` captures all terminal output. Clean it periodically to avoid disk bloat.
- Edit `nobot/config/soul.md` to customize the bot's personality (system prompt).
- If a config file gets corrupted, just delete it — the program recreates defaults on next launch.
- Bugs or suggestions? [Open an issue](https://github.com/Ravikov/NoBot/issues) — they're very welcome! 🎉

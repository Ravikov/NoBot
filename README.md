# NoBot

📖 English | [简体中文](./README.zh-CN.md)

A lightweight AI-powered WeChat chatbot built on the ClawBot interface.

> This is my first real project — built while learning Python. If something could be better, please bear with me, and if you have advice, I'd be truly grateful!

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

On first launch, the configuration wizard will walk you through setting up API URLs, keys, and model names. Everything is saved per-user to `nobot/config/<username>/config.json`.

### Quick Launch Scripts

| Platform | How |
|---|---|
| Windows | Double-click `Run.bat` |
| Linux / macOS | `./Run.sh` in terminal |

---

## Multi-User System

NoBot supports multiple independent users. Each user has their own:
- **Config** (`nobot/config/<username>/`)
- **Memory & history** (`nobot/memory/<username>/`)
- **ClawBot session** (`IMchat/clawbot/config/<username>/`)

At startup, you can select an existing user, create a new one, or delete one (except `main`). The `main` user is created automatically on first launch.

```
当前有如下用户:
名称: main,创建时间: 2026-06-07 13:31
请输入启动用户的名称,或输入delete来删除一个用户,输入creat来创建一个用户
>>>
```

When a non-`main` user starts for the first time, you have the option to copy the `main` user's API config as a starting point.

---

## Launch Modes

Select by number at startup:

| # | Mode | Description |
|---|---|---|
| 1 | Webhook | Flask server on `:5000` for third-party integration |
| 2 | CLI | Type questions directly in the terminal |
| 3 | Personal WeChat | ⏳ Unavailable for now |
| **4** | **WeChat ClawBot** | ✅ **Recommended** — scan QR code, then auto send & receive |
| **5** | **WebSocket** | ✅ WebSocket server on `ws://127.0.0.1:7323` — for custom clients |
| `set` | Config Wizard | Re-run the configuration guide |
| `save` / `load` | Backup / Restore | Dump or restore the current user's config |
| `del` | Clean logs | Delete `debug/bot.log` |

### Mode Details

**Webhook (1)** — Starts a Flask server on port 5000. Expects POST requests at `/webhook` with a JSON body containing `post_type: 'message'` and the message text. Returns a JSON reply.

**CLI (2)** — Interactive terminal session. Type questions, get answers. Press `Ctrl+C` to exit.

**WeChat ClawBot (4)** — Scans a QR code to log into WeChat via the iLink protocol, then automatically receives and replies to messages. Supports text, images, and videos.

**WebSocket (5)** — Starts a WebSocket server on `ws://127.0.0.1:7323`. Sends received messages to the LLM and returns the reply. If port 7323 is occupied, it auto-increments until a free port is found.

---

## Quick Commands

Send these in chat (or type in CLI mode):

| Command | Effect |
|---|---|
| `/rememory` | Clear the current user's conversation memory |
| `/memory` | Trigger immediate memory summarization |
| `/rehistory` | Clear the long-term history archive |

---

## Feature Status

| Feature | Status | Notes |
|---|---|---|
| Text message send & receive | ✅ | Done |
| Image receive + AI multimodal (type 2) | ✅ | Auto-downloaded & AES-decrypted, described by multimodal model |
| Video receive (type 5) | 🧪 | Experimental — download + description |
| Multi-message batching (type 9) | ✅ | Multiple messages accumulated before LLM call |
| Smart wait (LLM-decided) | ✅ | Uses secAPI to predict optimal accumulation time |
| Long-polling real-time fetch | ✅ | Done |
| QR code scan login | ✅ | Done |
| Intelligent search decision | ✅ | secAPI decides whether to enable web search per query |
| Multi-user support | ✅ | Independent configs, memory, and ClawBot sessions |
| Time injection | ✅ | Optionally injects current time into LLM context |
| Repeat mode (复读鸡) | ✅ | Echoes messages back (config flag `repeat`) |
| Image / video sending | ❌ | Pending iLink upload protocol |
| Personal WeChat (itchat) | ❌ | Deprecated, unavailable |

---

## Configuration

### Config Wizard (`set`)

Interactively configure all API endpoints and model parameters:

1. **Enable web search** — toggle `or_search`
2. **API credentials** for each model:
   - **Main model** (`API`) — primary LLM for replies
   - **Auxiliary model** (`secAPI`) — used for search decision & smart wait
   - **Web search model** (`searchAPI`) — LLM with search capability
   - **Multimodal model** (`multimodalAPI`) — image/video understanding
   - (Image generation model reserved, not yet active)
3. **Main model parameters**:
   - `temperature` (0–2, default 1.0)
   - `max_history_turns` (default 20) — memory compression triggers after this many turns
   - `or_time_feel` — whether to inject current time into LLM context

### Key Config Fields (`config/<username>/config.json`)

| Field | Default | Description |
|---|---|---|
| `API` / `secAPI` / `searchAPI` / `multimodalAPI` / `imageAPI` | — | Model configs: `url`, `key`, `name` |
| `max_tokens` | 1500 | Max generation tokens |
| `temperature` | 1.0 | LLM temperature |
| `prompt_file` | `"soul"` | Prompt file name (`.md` appended) |
| `max_history_turns` | 20 | Turns before memory compression |
| `save_turns` | 10 | Undocumented |
| `wait` | 8 | Base wait time (seconds) for message accumulation |
| `llm_decide_wait` | true | Use secAPI to dynamically adjust wait time |
| `or_search` | true | Enable web search |
| `or_time_feel` | true | Inject current time into context |
| `wash_comma` | false | Replace Chinese commas with spaces |
| `repeat` | false | Echo mode (复读鸡) |
| `debug` | false | Append cache hit rate to responses |
| `txt_wash` | `["*", "\\n", "。"]` | Characters to strip from replies |

### System Prompt

Edit `nobot/config/<username>/soul.md` (or the file specified by `prompt_file`) to customize the bot's personality.

---

## Project Structure

```
NoBot/
├── main.py                              # Entry point
├── Run.bat / Run.sh                     # Quick launcher scripts
├── requirements.txt                     # Python dependencies
├── check.py                             # Pre-launch integrity check
│
├── message/                             # Message protocol layer
│   ├── msg.py                           # Base classes: Message, ReplyIn, ReplyOut
│   └── clawbot/
│       └── clawbotmsg.py                # WechatBotMessage base class
│
├── IMchat/                              # WeChat ClawBot implementation
│   └── clawbot/
│       ├── clawbot.py                   # Main controller: login, token, main loop
│       ├── clawbot_common.py            # Utilities: config, headers, UIN
│       ├── login.py                     # ClawBot login (QR fetch, scan polling)
│       ├── config/<username>/           # Per-user ClawBot session cache (auto-generated)
│       │   └── clawbot.json
│       ├── debug/
│       │   └── request.json             # Latest API request dump
│       ├── getmsg/                      # Message receiving
│       │   ├── getupdate.py             # Long-polling API
│       │   ├── handlemsg.py             # Message routing & content extraction
│       │   ├── mediagetter.py           # Media download & AES decryption
│       │   ├── waitimer.py              # Smart wait decision (LLM-powered)
│       │   └── replymsg.py              # Reply engine bridge
│       └── sendmsg/                     # Message sending
│           ├── send.py                  # Split-message sending
│           └── sendtyping.py            # Typing indicator
│
├── nobot/                               # Core logic
│   └── src/
│       ├── common.py                    # Paths, config loading, history I/O, defaults
│       ├── guide.py                     # CLI configuration wizard
│       ├── core/
│       │   ├── get_reply/
│       │   │   ├── reply.py             # ReplyHandler: routing & reply generation
│       │   │   └── touch_llm.py         # Low-level API calls (text / multimodal / web search)
│       │   └── mem/
│       │       └── memory.py            # Memory compression & summarization
│       └── user/
│           ├── user.py                  # Multi-user system: selection, creation, deletion
│           └── userlist.json            # User registry
│
├── nobot/config/<username>/             # Per-user API config
│   ├── config.json                      # API config (URL / Key / model name)
│   ├── config.json.bak                  # Backup
│   └── soul.md                          # System prompt (bot personality)
│
├── nobot/memory/<username>/
│   ├── memory.json                      # Conversation history & memory
│   └── longhistory.json                 # Long-term memory archive
│
├── websocket/
│   └── server.py                        # WebSocket server (mode 5)
│
├── debug/                               # Debug & logs
│   ├── log.py                           # Logging utility
│   ├── bot.log                          # Runtime log
│   ├── states.json                      # Token usage stats
│   └── response.json                    # Latest raw API response
│
└── etc/
    └── start_ways.py                    # Launch mode dispatcher
```

---

## Notes

- `debug/bot.log` captures all terminal output — clean it periodically via the `del` startup command to avoid disk bloat.
- Edit `nobot/config/<username>/soul.md` to customize the bot's personality (system prompt).
- If a config file gets corrupted, just delete it — the program recreates defaults on next launch.
- Unsupported message types are logged and returned as-is.
- Bugs or suggestions? [Open an issue](https://github.com/Ravikov/NoBot/issues) — they're very welcome! 🎉

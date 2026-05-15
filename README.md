# NoBot

📖 English | [简体中文](./README.zh-CN.md)

**This README was translated by DeepSeek,the original document is in Chinese,so if there are any inaccuracies, please refer to the original Chinese version (`README.zh-CN.md`).**

## A Lightweight Simple AI Chatbot

This project is developed in Python, using the `requests` library to call APIs instead of the OpenAI SDK (mainly because I'm still a beginner and haven't figured it out yet).

This project was built step by step while I was learning, so there are still many things I only half understand. If any kind experienced developer sees this repository, issues are more than welcome.

Currently, configuration settings are typically done through command-line guidance. I may try to develop a WebUI in the future.

## Quick Start

**This project is developed in Python. Please ensure you have Python 3.10 or higher installed.**

- It is recommended to run from source. You can download the latest source code zip package from Releases, or use the following git command:
  ```cmd
  git clone https://github.com/Ravikov/NoBot.git
  ```
- After obtaining the source code, navigate to the project root directory (the folder containing `main.py`). Right-click inside the folder, open it in a terminal, and run `python -u main.py`.

### Configuration

- The first time you start the program, it will automatically enter configuration guidance. Follow the prompts to enter the URL, API key, and model name for the 'Main Model', 'Auxiliary Model', and 'Web Search Model'.
- After configuring the API information, you will be prompted to set some other miscellaneous options. Just accept the defaults if you're unsure.
- *If you need to add a system prompt after configuration, please write it in `config/role_prompt.txt`.*

### Usage

- After configuration, you can exit the program with `Ctrl+C` (you can do this at any stage), then restart.
- Upon restart, you'll enter the runtime mode selection menu. Choose the appropriate mode by entering its number. Generally, it's recommended to select "WeChat ClawBot".
- The first time you start ClawBot, it will automatically obtain a QR code. Scan it with WeChat to log in. Once the command line shows "Waiting for long polling messages...", you can start chatting.
- *Due to some latency in the iLink API, response times may be a bit slow. I will try to optimize this in the future, but the effect may not be perfect.*
- **Image messages can now be received and saved locally, but multimodal visual replies are not yet supported.** Images are saved as `get_image_timestamp.jpg` in the project root directory.

## How to Use

The `config` directory contains some basic configuration files (not included in the source code to prevent leaking sensitive information).

**After obtaining the source code, please run `main.py` first. The program will automatically create configuration files with default formatting.**

### `config/`

- `config.json` contains model-related settings:
  - `"API"`: Main model.
  - `"secAPI"`: Auxiliary model.
  - `"searchAPI"`: Web search model (be sure to use a model that supports web search, otherwise performance may be disappointing).
  
  Other settings (like `temperature`, etc.) control the main model. There are also some prompts for the auxiliary model. It is generally recommended not to change them, especially the `"or_search_prompt"` field. **The model must return only `1` or `0`. If it returns anything else, the program will crash!**

- `wechat_clawbot.json` contains information about the iLink interface. **Do not** configure this manually. It's best not to change it. If you break it by accident, just delete it, and the program will recreate a default one next time it starts.

- `role_prompt.txt` is where you can write the system prompt for the bot.

### `debug/`

This directory mainly contains debugging files. Regular users can ignore it.

Please note that `debug/` contains a `bot.log` file where all the logs shown in the terminal are stored. It is recommended to clean it up periodically (just delete the file) to prevent excessive disk usage.

### `memory/`

This directory contains only one file: `memory.json`, which stores conversation history and periodic memory summaries. If you want to clear the bot's memory, simply delete this file.

### `src/`

This is the source code. Main file responsibilities:

- `touch_llm.py` — Low-level LLM API calls
- `reply.py` — Message routing: normal chat vs quick commands
- `memory.py` — Memory compression using the auxiliary model
- `common.py` — Global paths and config loading
- `start/wechat_clawbot.py` — Full WeChat ClawBot logic: login, receive, reply
- `start/start_ways.py` — Other startup modes (webhook, CLI, etc.)
- `guide.py` — Command-line configuration wizard

### Quick Commands

Currently only two quick commands are supported. You can use them either in the chat interface or from the command line:

- `/rememory` - Clear the bot's memory
- `/memory` - Manually trigger memory summarization

## Closing Words

This is my first real project (and also a learning project). I learned as I built — whenever I got stuck, I went and learned what I needed. So if some parts aren't well done, I kindly ask you to be understanding. If this project isn't useful for you, feel free to ignore it. But I would truly appreciate it if someone could offer me some guidance. Thank you!
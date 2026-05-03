# NoBot

📖 English | [简体中文](./README.zh-CN.md)

**This README was translated by DeepSeek,the original document is in Chinese,so if there are any inaccuracies, please refer to the original Chinese version (`README.zh-CN.md`).**

## A Lightweight Simple AI Chatbot

This project is developed in Python, using the `requests` library to call APIs instead of the OpenAI SDK (mainly because I'm still a beginner and haven't figured it out yet).

This project was built step by step while I was learning, so there are still many things I only half understand. If any kind experienced developer sees this repository, issues are more than welcome.

Currently, configuration settings can only be changed by modifying files (since I haven't learned how to do it properly yet). I may try to develop a WebUI in the future.

## How to Use

There are some basic configuration files in the `config/` directory (they are not included in the source code to avoid leaking sensitive information).

**After obtaining the source code, please run `main.py` first. The program will automatically create configuration files with default formatting.**

### `config/`

- `config.json` contains some model-related settings:
  - `"API"`: Configuration for the main model.
  - `"secAPI"`: Configuration for the auxiliary model.
  - `"searchAPI"`: Configuration for the web search model. Be sure to use a model that supports web search, otherwise performance may be disappointing.
  
  Other settings (like `temperature`, etc.) control the main model. There are also some prompt words for the auxiliary model. It is generally recommended not to change them, especially the `"or_search_prompt"` field. **The model must return only `1` or `0`. If it returns anything else, the program will crash.**

- `wechat_clawbot.json` contains information about the iLink interface. **Do not** modify this manually. If something breaks, just delete it and the program will recreate it with default settings the next time it starts.

- `role_prompt.txt` is where you can write the system prompt for the bot.

### `debug/`

This directory mainly contains debugging files. Regular users can ignore it.

Please note that `debug/` contains a `bot.log` file where all the logs shown in the terminal are stored. It is recommended to clean it up periodically (just delete the file) to prevent excessive disk usage.

### `memory/`

This directory contains only one file: `memory.json`, which stores conversation history and periodic memory summaries. If you want to clear the bot's memory, simply delete this file.

### `src/`

This is the source code. No further explanation needed.

### Quick Commands

Currently only two quick commands are supported. You can use them either in the chat interface or from the command line:

- `/rememory` - Clear the bot's memory
- `/memory` - Manually trigger memory summarization

## Closing Words

This is the work of a 15-year-old, created through trial and error. It is also my first real project. I learned as I built — whenever I got stuck, I went and learned what I needed. So if some parts aren't well done, I kindly ask you to be understanding. If the project isn't useful for you, feel free to ignore it. But I would truly appreciate it if someone could offer me some guidance. Thank you!
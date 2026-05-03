import json
import time

# 日志
def log(msg, level="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    with open("debug/bot.log", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        f.flush()
    print(log_line, flush=True)

# 配置（只读一次）
with open("config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 记忆（基础读写）
MEMORY_FILE = "memory/memory.json"

def load_history():
    with open(MEMORY_FILE, 'r', encoding='UTF-8') as f:
        return json.load(f)

def save_history(history):
    with open(MEMORY_FILE, 'w', encoding='UTF-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
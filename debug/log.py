import time
import json
import pathlib

# 日志
def log(msg, level="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if len(msg) >= 1000:
        msg = msg[:1000]+'......'
    log_line = f"[{timestamp}] [{level}] {msg}"
    with open("debug/bot.log", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        f.flush()
    print(log_line, flush=True)

def debug_log(msg):
    with open(pathlib.Path(__file__).parent.parent / 'nobot' / 'config' / 'config.json', "r", encoding="utf-8") as f:
        config = json.load(f)
    if config.get('debug', False):
        log(msg, level="DEBUG")
    else:
        pass
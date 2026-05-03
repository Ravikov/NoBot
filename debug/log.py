import time

# 日志
def log(msg, level="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    with open("debug/bot.log", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        f.flush()
    print(log_line, flush=True)
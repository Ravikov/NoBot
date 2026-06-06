import time
import json
import pathlib
import sys
import traceback

# 日志
def log(msg, level="INFO"): #过长时写入完整信息 终端提示简略信息
    msg = str(msg)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if len(msg) >= 500:
        short_msg = msg[-300:]
        log_line  = msg[:500]+'......'+msg[-500:]
        short_line = f"[{timestamp}] [{level}] ...({len(msg)}chars){short_msg}"
    else:
        short_line = None
        log_line = f"[{timestamp}] [{level}] {msg}"
    with open("debug/bot.log", "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        f.flush()
    print(short_line if short_line else log_line, flush=True)

def debug_log(msg):
    with open(pathlib.Path(__file__).parent.parent / 'nobot' / 'config' / 'config.json', "r", encoding="utf-8") as f:
        config = json.load(f)
    if config.get('debug', False):
        log(msg, level="DEBUG")
    else:
        pass

# 捕获未处理的异常（Python 报错）并写入日志
def _log_exception(exc_type, exc_value, exc_tb):
    log('程序崩溃，错误信息如下：', level='ERROR')
    for line in traceback.format_exception(exc_type, exc_value, exc_tb):
        log(line.rstrip('\n'), level='ERROR')

sys.excepthook = _log_exception
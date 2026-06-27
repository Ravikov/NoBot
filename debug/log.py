import time
import json
import pathlib
import sys
import traceback

# 默认日志文件（当 common.py 尚未加载时的回退路径）
_DEFAULT_LOGFILE = pathlib.Path(__file__).parent / 'start.log'

def _resolve_logfile():
    """延迟获取 LOGFILE，避免循环导入。
    在模块加载时 common.py 可能还没执行到 LOGFILE 定义行，
    所以推迟到 log() 被调用时才去获取。"""
    try:
        from nobot.src.common import LOGFILE
        return LOGFILE
    except (ImportError, AttributeError):
        return _DEFAULT_LOGFILE

# 日志
def log(msg, level="INFO", logfile=None):
    """
    写入日志。
    
    参数:
        msg    : 日志内容
        level  : 日志级别 (INFO/DEBUG/WARN/ERROR)
        logfile: 指定日志文件路径。为 None 时自动选用当前用户的 LOGFILE。
                 传入 logfile=某个路径 即可写入对应用户的日志。
    """
    logfile = logfile or _resolve_logfile()
    msg = str(msg)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if len(msg) >= 500:
        short_msg = msg[-300:]
        log_line  = msg[:500]+'......'+msg[-500:]
        short_line = f"[{timestamp}] [{level}] ...({len(msg)}chars){short_msg}"
    else:
        short_line = None
        log_line = f"[{timestamp}] [{level}] {msg}"
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        f.flush()
    print(short_line if short_line else log_line, flush=True)

def debug_log(msg):
    try:
        from nobot.src.common import CONFIG_FILE
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except:
        config = {}
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
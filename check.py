import json
import os
from collections import deque # deque可以高效地读取日志末行
from pathlib import Path
from debug.log import log
from nobot.src.common import *


def check():
    log('执行check...')

    N = 0
    # 检查目录完整性
    filedirs = [
        ROOT/'config',
        ROOT/'memory',
        ROOT.parent / 'IMchat' / 'clawbot' / 'config',
    ]
    for d in filedirs:
        debug_log(f'检查{d}目录是否存在...')
        filedir = Path(d)
        if not filedir.exists():
            N+=1
            log(f'创建{d}目录...')
            filedir.mkdir(parents=True)
        else:
            debug_log(f'{d}存在')
    # 检查文件完整性
    files = [
        CONFIG_FILE,
        CONFIGBAK_FILE,
        CLAWBOT_FILE,
        PROMPT_FILE,
        LOGFILE,
        RESPONSEJSON_FILE,
        MEMORY_FILE,
        LONGHISTORY_JSON_FILE,
        REQUEST_JSON_FILE
    ]

    def w_json(file_name,default):
        with open(file_name,'w',encoding='utf-8') as f:
            json.dump(default,f,ensure_ascii=False,indent=2)
    def check_file(file):
        nonlocal N
        if not file.exists():
            N+=1
            log(f'{file.name}不存在,尝试创建{file}...')
            file.parent.mkdir(parents=True,exist_ok=True)
            with open(file,'w',encoding='utf-8') as f:
                pass
            if file in [CONFIG_FILE,CLAWBOT_FILE,MEMORY_FILE,LONGHISTORY_JSON_FILE]:
                file = file
                log(f'为{file}写入默认值...')
                if file == CONFIG_FILE:
                    w_json(file,DEFAULT_CONFIG)
                elif file == CLAWBOT_FILE:
                    w_json(file,DEFAULT_WECHATCLAW)
                elif file == MEMORY_FILE:
                    w_json(file,DEFAULT_MEMORY)
                elif file == LONGHISTORY_JSON_FILE:
                    w_json(file,DEFAULT_LONGHISTORY)
        else:
            pass


    # log大小检查
    def log_check():
        log('检查日志文件大小...')
        size = os.path.getsize(LOGFILE)
        log(f'当前日志文件大小: {size/(1024*1024):.2f} MB')
        if size > 10*1024*1024:
            log('日志文件过大,尝试清理...')
            with open(LOGFILE,'r',encoding='utf-8') as f:
                final_lines = deque(f,maxlen=1000)
            with open(LOGFILE,'w',encoding='utf-8') as f:
                f.writelines(final_lines)
            log('日志文件清理完毕')
        else:
            log('日志文件大小正常')

    log('校验配置文件完整性...')
    log('特别提醒: 如果发现某些配置文件读取时报错,尝试删除相应文件后重新运行程序!')
    for f in files:
        debug_log(f'检查文件{f}')
        check_file(Path(f))
    log(f'校验完毕,修复{N}个文件')
    log_check()
    return N
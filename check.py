from pathlib import Path
from debug.log import log
from nobot.src.common import *
import json

def check():
    log('执行check...')
    # 配置文件默认格式
    DEFAULT_CONFIG = {
        "API":{
            "key": "",
            "url": "https://api.deepseek.com/v1/chat/completions",
            "name": "deepseek-v4-flash"
        },
        "secAPI":{
            "key": "",
            "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "name": "qwen3.6-flash"
        },
        "searchAPI":{
            "key": "",
            "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "name": "qwen3.6-flash"
        },
        "multimodalAPI": {
            "key": "",
            "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "name": "qwen3.6-flash"
        },
        "imageAPI": {
            "key": "",
            "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "name": "qwen3.6-flash"
        },
        "max_tokens": 1500,
        "temperature": 1.0,
        "prompt_file":"soul",
        "max_history_turns": 20,
        "save_turns": 10,
        "wait": 8,
        "memory_prompt": "请将用户提供的对话消息记录和旧的记忆总结成新的记忆,根据不同信息的权重可以有适当的删减,但主要事件不应该改动",
        "or_search_prompt": [
            {"role": "user","content": "请根据提示词判断回答该内容是否需要联网搜索 如果需要 请回复1 如果不需要 请回复0 你的回答必须遵守:只能出现0或1 不能有其他任何字符"}
        ],
        "txt_wash": [
            "*","\\n","。"
        ],
        "or_time_feel": True,
        "or_search": True,
        "non_setup": True,
        "debug": False,
        "llm_decide_wait": True
    }

    DEFAULT_WECHATCLAW = {
    "baseurl": "https://ilinkai.weixin.qq.com",
    "token": "",
    "botid": "",
    "userid": "",
    "cursor": "",
    "clientid": ""
    }

    DEFAULT_MEMORY = {
        "history": [
        {
            "role": "user",
            "content": "对话格式举例,回复格式请遵从于此"
        },
        {
            "role": "assistant",
            "content": "在在在#我刚在玩游戏#你呢 你干啥呢"
        }
        ],
        "memory": [
            {
            "role": "system",
            "content": "[过往记忆]"
            }
        ],
        "turns": 0
    }

    DEFAULT_STATES = {
        "all_tokens": 0
    }

    N = 0
    # 检查目录完整性
    filedirs = [
        'config',
        'memory'
    ]
    for d in filedirs:
        log(f'检查{d}目录是否存在...')
        filedir = Path(d)
        if not filedir.exists():
            N+=1
            log(f'创建{d}目录...')
            filedir.mkdir(parents=True)
        else:
            log(f'{d}存在')
    # 检查文件完整性
    files = [
        CONFIG_FILE,
        CONFIGBAK_FILE,
        CLAWBOT_FILE,
        PROMPT_FILE,
        ROOT.parent / 'debug' / 'bot.log',
        RESPONSEJSON_FILE,
        STATEJSON_FILE,
        MEMORY_FILE
    ]
    def w_json(file_name,default):
        with open(file_name,'w',encoding='utf-8') as f:
            json.dump(default,f,ensure_ascii=False,indent=2)
    def check_file(file):
        nonlocal N
        if not file.exists():
            N+=1
            log(f'{file.name}不存在,尝试创建{file}...')
            with open(file,'w',encoding='utf-8') as f:
                pass
            if file in [CONFIG_FILE,CLAWBOT_FILE,STATEJSON_FILE,MEMORY_FILE]:
                file = file
                log(f'为{file}写入默认值...')
                if file == CONFIG_FILE:
                    w_json(file,DEFAULT_CONFIG)
                elif file == CLAWBOT_FILE:
                    w_json(file,DEFAULT_WECHATCLAW)
                elif file == STATEJSON_FILE:
                    w_json(file,DEFAULT_STATES)
                elif file == MEMORY_FILE:
                    w_json(file,DEFAULT_MEMORY)
        else:
            pass
    log('校验配置文件完整性...')
    log('特别提醒: 如果发现某些配置文件读取时报错,尝试删除相应文件后重新运行程序!')
    for f in files:
        check_file(Path(f))
    log(f'校验完毕,修复{N}个文件')
    return N
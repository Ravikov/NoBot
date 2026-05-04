from pathlib import Path
from debug.log import log
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
        "max_tokens": 2048,
        "temperature": 1.2,
        "prompt_file":"role_prompt",
        "max_history_turns": 20,
        "memory_prompt": "请将用户提供的对话消息记录和旧的记忆总结成新的记忆,根据不同信息的权重可以有适当的删减,但主要事件不应该改动",
        "or_search_prompt": [
            {"role": "user","content": "请根据提示词判断回答该内容是否需要联网搜索 如果需要 请回复1 如果不需要 请回复0 你的回答必须遵守:只能出现0或1 不能有其他任何字符"}
        ],
        "txt_wash": [
            "*"
        ],
        "or_time_feel": True,
        "non_setup": True
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
    "history": [],
    "memory": [
        {
        "role": "system",
        "content": ""
        }
    ],
    "turns": 0
    }

    DEFAULT_STATES = {
        "all_tokens": 0
    }

    # 检查目录完整性
    filedirs = [
        'config',
        'memory'
    ]
    for d in filedirs:
        log(f'检查{d}目录是否存在...')
        filedir = Path(d)
        if not filedir.exists():
            log(f'创建{d}目录...')
            filedir.mkdir(parents=True)
        else:
            log(f'{d}存在')
    # 检查文件完整性
    files = [
        'config/config.json',
        'config/config.json.bak',
        'config/wechat_clawbot.json',
        'config/role_prompt.txt',
        'debug/bot.log',
        'debug/response.json',
        'debug/states.json',
        'memory/memory.json'
    ]
    def w_json(file_name,default):
        with open(file_name,'w',encoding='utf-8') as f:
            json.dump(default,f,ensure_ascii=False,indent=2)
    N = 0
    def check_file(file):
        nonlocal N
        if not file.exists():
            N+=1
            log(f'{file.name}不存在,尝试创建{file}...')
            with open(file,'w',encoding='utf-8') as f:
                pass
            if str(file) in ['config\config.json','config\wechat_clawbot.json','debug\states.json','memory\memory.json']:
                file = str(file)
                log(f'为{file}写入默认值...')
                match file:
                    case 'config\config.json':
                        w_json(file,DEFAULT_CONFIG)
                    case 'config\wechat_clawbot.json':
                        w_json(file,DEFAULT_WECHATCLAW)
                    case 'debug\states.json':
                        w_json(file,DEFAULT_STATES)
                    case 'memory\memory.json':
                        w_json(file,DEFAULT_MEMORY)
                    case _:
                        pass
        else:
            pass
    log('校验配置文件完整性...')
    log('特别提醒: 如果发现某些配置文件读取时报错,尝试删除相应文件后重新运行程序!')
    for f in files:
        check_file(Path(f))
    log(f'校验完毕,修复{N}个文件')
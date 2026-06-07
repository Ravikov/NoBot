import json
import pathlib
from debug.log import *
from nobot.user.user import usrobj

usrname = usrobj.name
debug_log(f'本次启动的用户名: {usrname}')
# 配置文件全局路径
ROOT = pathlib.Path(__file__).parent.parent
log(f'工作目录 {ROOT}')
CONFIG_FILE = ROOT / 'config' / usrname / 'config.json'
# 配置
def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
try:
    a = load_config() # a为代替config的变量
except FileNotFoundError:
    a = {'prompt_file':'soul'}

prompt_file = a['prompt_file']+'.md'
PROMPT_FILE = ROOT / 'config' / usrname / prompt_file
CONFIGBAK_FILE = ROOT / 'config' / usrname / 'config.json.bak'
CLAWBOT_FILE = ROOT.parent / 'IMchat' / 'clawbot' / 'config' / usrname / 'clawbot.json'
MEMORY_FILE = ROOT / 'memory' / usrname / 'memory.json'
RESPONSEJSON_FILE = ROOT.parent / 'debug' / 'response.json'
LONGHISTORY_JSON_FILE = ROOT / 'memory' / usrname / 'longhistory.json'
REQUEST_JSON_FILE = ROOT.parent / 'IMchat' / 'clawbot' / 'debug' / 'request.json'

# 设置项列举
llm_list = [
    '主模型',
    '辅助模型',
    '联网模型',
    '多模态理解模型',
    # '生图模型'
]
project_list = [
    'url',
    'key',
    'name'
]
mainllm_settings = [
    'temperature',
    '最大上下文轮数',
    '是否启用时间注入'
]

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
        "name": "qwen3.7-plus"
    },
    "searchAPI":{
        "key": "",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "name": "qwen3.7-plus"
    },
    "multimodalAPI": {
        "key": "",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "name": "qwen3.7-plus"
    },
    "imageAPI": {
        "key": "",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "name": "qwen3.7-plus"
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
    "llm_decide_wait": True,
    "wash_comma": False,
    "repeat": False
}

DEFAULT_WECHATCLAW = {
"baseurl": "https://ilinkai.weixin.qq.com",
"token": "",
"botid": "",
"userid": "",
"cursor": "",
"clientid": "",
"name": "main"
}

DEFAULT_MEMORY = {
    "history": [],
    "memory": [
        {
        "role": "system",
        "content": "[过往记忆]"
        }
    ],
    "turns": 0
}

DEFAULT_LONGHISTORY = {
    "history":[]
}

# 记忆（基础读写）
MEMORY_JSON_FILE = MEMORY_FILE

def load_history():
    with open(MEMORY_JSON_FILE, 'r', encoding='UTF-8') as f:
        return json.load(f)

def save_longhistory(longhistory):
    with open(LONGHISTORY_JSON_FILE, 'w', encoding='UTF-8') as f:
        json.dump(longhistory, f, ensure_ascii=False, indent=2)

def save_history(history):
    with open(MEMORY_JSON_FILE, 'w', encoding='UTF-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    with open(LONGHISTORY_JSON_FILE, 'r', encoding='UTF-8') as f:
        longhistory = json.load(f)
    longhistory['history'] += history['history'][:-2]
    save_longhistory(longhistory)
    

# retry装饰器
def retry(obj,trytime=3):
    def wrapper(*args,**kwargs):
        for i in range(trytime):
            try:
                return obj(*args,**kwargs)
            except Exception as e:
                log(f'执行{obj.__name__}发生错误: {e}, 正在重试...({i+1}/{trytime})','Error')
        log(f'执行{obj.__name__}失败: 已达最大重试次数 {trytime}', 'Error')
    return wrapper
import json
import pathlib
from debug.log import *

# 配置文件全局路径
ROOT = pathlib.Path(__file__).parent.parent
log(f'工作目录 {ROOT}')
CONFIG_FILE = ROOT / 'config' / 'config.json'
# 配置
def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
try:
    a = load_config() # a为代替config的变量
except FileNotFoundError:
    a = {'prompt_file':'soul'}

prompt_file = a['prompt_file']+'.md'
PROMPT_FILE = ROOT / 'config' / prompt_file
CONFIGBAK_FILE = ROOT / 'config' / 'config.json.bak'
CLAWBOT_FILE = ROOT.parent / 'IMchat' / 'clawbot' / 'config' / 'wechat_clawbot.json'
MEMORY_FILE = ROOT / 'memory' / 'memory.json'
STATEJSON_FILE = ROOT.parent / 'debug' / 'states.json'
RESPONSEJSON_FILE = ROOT.parent / 'debug' / 'response.json'

# 设置项列举
llm_list = [
    '主模型',
    '辅助模型',
    '联网模型',
    '多模态理解模型',
    '生图模型'
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

# 记忆（基础读写）
MEMORY_JSON_FILE = MEMORY_FILE

def load_history():
    with open(MEMORY_JSON_FILE, 'r', encoding='UTF-8') as f:
        return json.load(f)

def save_history(history):
    with open(MEMORY_JSON_FILE, 'w', encoding='UTF-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
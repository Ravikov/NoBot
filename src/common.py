import json
import pathlib

# 配置文件全局路径
ROOT = pathlib.Path(__file__).parent.parent
CONFIG_FILE = ROOT / 'config' / 'config.json'
# 配置（只读一次）
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

prompt_file = config['prompt_file']+'.txt'
PROMPT_FILE = ROOT / 'config' / prompt_file
CONFIGBAK_FILE = ROOT / 'config' / 'config.json.bak'
CLAWBOT_FILE = ROOT / 'config' / 'wechat_clawbot.json'
MEMORY_FILE = ROOT / 'memory' / 'memory.json'
STATEJSON_FILE = ROOT / 'debug' / 'states.json'
RESPONSEJSON_FILE = ROOT / 'debug' / 'response.json'

# 设置项列举
llm_list = [
    '主模型',
    '辅助模型',
    '联网模型'
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
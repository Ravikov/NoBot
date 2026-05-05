import json
import pathlib

# 配置文件全局路径
ROOT = str(pathlib.Path(__file__).parent.parent)
CONFIG_FILE = ROOT + '\config'
MEMORY_FILE = ROOT + '\memory'
DEBUG_FILE = ROOT + '\debug'

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

# 配置（只读一次）
with open(CONFIG_FILE+'\config.json', "r", encoding="utf-8") as f:
    config = json.load(f)

# 记忆（基础读写）
MEMORY_JSON_FILE = MEMORY_FILE+'\memory.json'

def load_history():
    with open(MEMORY_JSON_FILE, 'r', encoding='UTF-8') as f:
        return json.load(f)

def save_history(history):
    with open(MEMORY_JSON_FILE, 'w', encoding='UTF-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
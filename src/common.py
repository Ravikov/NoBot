import json

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
with open("config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 记忆（基础读写）
MEMORY_FILE = "memory/memory.json"

def load_history():
    with open(MEMORY_FILE, 'r', encoding='UTF-8') as f:
        return json.load(f)

def save_history(history):
    with open(MEMORY_FILE, 'w', encoding='UTF-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
import json
from src.touch_llm import sec_llm
from src.common import config
from debug.log import log

def load_history():
    with open('memory.json','r',encoding='UTF-8') as f:
        history = json.load(f)
    return history
def save_history(history):
    with open('memory.json','w',encoding='UTF-8') as f:
        json.dump(history,f,ensure_ascii=False,indent=2)
    return 0

def set_memory():
    mem = load_history()
    memory = sec_llm(
        0,
        mem['memory'],
        [{'role': 'system','content': config['memory_prompt']}],
        mem['history'],
        [{'role': 'user','content': '将上文总结'}]
    )
    if memory == 1:
        t = '记忆总结失败,请参考api错误码'
        log(t,'error')
        return t,1
    else:
        mem['history'] = []
        mem['turns'] = 0
        mem['memory'] = [{"role": "system", "content": f"{memory}"}]
        save_history(mem)
        t = '总结记忆完毕'
        log(t)
        return t,0
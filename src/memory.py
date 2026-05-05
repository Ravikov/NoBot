from src.touch_llm import sec_llm
from src.common import config,load_history,save_history
from debug.log import log

def set_memory():
    mem = load_history()
    memory = sec_llm(
        0,
        mem['memory']+
        [{'role': 'system','content': config['memory_prompt']}]+
        mem['history']+
        [{'role': 'user','content': '将对话记录进行记忆性总结,要有类似记忆深度的因素在内,回答中不要有任何无效成分,只能是对记忆的描述,不要换行'}]
    )
    if memory == 1:
        t = '记忆总结失败,请参考api错误码'
        log(t,'error')
        return t,1
    else:
        mem['history'] = [
            {
                "role": "user",
                "content": "对话格式举例"
            },
            {
                "role": "assistant",
                "content": "在在在#我刚在玩游戏#你呢 你干啥呢"
            }
        ]
        mem['turns'] = 0
        mem['memory'] = [{"role": "system", "content": f"[过往记忆]{memory}"}]
        log(str(mem))
        save_history(mem)
        t = '总结记忆完毕'
        log(t)
        t = [t,]
        return t,0
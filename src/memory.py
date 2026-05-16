from src.touch_llm import sec_llm
from src.common import config,load_history,save_history
from debug.log import log

def set_memory():
    mem = load_history()
    memory = sec_llm(
        0,
        [{'role': 'system','content': str(mem)}]+
        [{'role': 'system','content': config['memory_prompt']}]+
        [{'role': 'user','content': '将对话记录进行记忆性总结,要有类似记忆深度的因素在内,一定注意时间权重,注意分清身份,回答中不要有任何无效成分,只能是对记忆的描述,不要换行,对于多媒体消息不需要过度总结,简要带过即可'}]
    )
    if memory is None:  # sec_llm 失败时返回 None (Edited by DeepSeek TUI)
        t = '记忆总结失败,请参考api错误码'
        log(t,'error')
        return t,1
    else:
        mem['history'] = mem['history'][-10:]
        mem['turns'] = 0
        mem['memory'] = [{"role": "system", "content": f"[过往记忆]{memory}"}]
        save_history(mem)
        t = '总结记忆完毕'
        log(t)
        t = [t,]
        return t,0
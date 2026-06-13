from nobot.src.core.llm.touch_llm import TouchLLM
from nobot.src.common import *
from debug.log import log

def set_memory():
    config = load_config()
    mem = load_history()
    toucher = TouchLLM(
        msg=None,
        llm='secAPI',
        sysmsg=(
                [{'role': 'system','content': str(mem)}]+
                [{'role': 'system','content': config['memory_prompt']}]+
                [{'role': 'user','content': """将对话记录进行记忆性总结,要有类似记忆深度的因素在内,
                                            一定注意时间权重,注意分清身份,回答中不要有任何无效成分,只能是对记忆的描述,
                                            不要换行,对于多媒体消息不需要过度总结,简要带过即可"""}]
            )
        )
    toucher.touch()
    memory = toucher.result
    if memory['delay'] == -1:
        t = '记忆总结失败,请参考api错误码'
        log(t,'error')
        return {'type': 0, 'msg': [t], 'delay': 0}
    else:
        mem['history'] = mem['history'][-10:]
        mem['turns'] = 0
        mem['memory'] = [{"role": "system", "content": f"[过往记忆]{memory['msg']}"}]
        save_history(mem)
        t = '总结记忆完毕'
        log(t)
        t = [t,]
        return {'type': 1, 'msg': t, 'delay': 0}
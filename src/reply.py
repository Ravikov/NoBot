from src.common import load_history,save_history,config
from src.memory import set_memory
from src.touch_llm import fst_llm,sec_llm,search_api
from debug.log import log

def reply(mes):
    if not mes:
        log('消息为空')
        return "消息异常"
    else:
        pass

    if mes[0] == '/':
        match mes[1:]:
            case 'rememory':
                history = load_history()
                history['history'] = []
                history['memory'] = [{"role": "system","content": ""}]
                history['turns'] = 0
                save_history(history)
                log('清除记忆')
                return '清除记忆成功',0
            case 'memory':
                log('记忆总结...')
                re,e = set_memory()
                if e:
                    return {'reply': re}
                else:
                    return {'reply': re}
            case _:
                log('未知指令,本次输入略过')
                return '未知的指令',0
    else:
        log('调用辅助模型判断联网功能...')
        or_search = sec_llm(
            0,
            [{'role': 'system','content': mes}],
            config['or_search_prompt']
        )
        log(f'判断完毕,结果: {or_search}')
        if or_search == '1':
            log('调用联网搜索模型...')
            result,state,ms,orgin_result = search_api(mes)
        elif or_search == '0':
            log('调用大模型api...')
            result,state,ms,orgin_result = fst_llm(mes)
        else:
            log('辅助模型输出错误')
            return 1,0

        log('状态码审查...')
        if state == 200:
            log(f'状态正确,提交回复: {result}')

            history = load_history()
            if history.get('turns') >= config.get('max_history_turns') - 1:
                log('需要进行记忆总结,正在调用api')
                set_memory()
            else:
                pass

            # 输出清洗
            text = ''
            for i in result:
                if i in config['txt_wash']:
                    pass
                else:
                    text = text+i
            result = text

            log('写入记忆...')
            history = load_history()
            history['history'].append({"role": "user", "content": mes})
            history['history'].append({"role": "assistant", "content": result})
            history['turns'] = history.get('turns') + 1
            save_history(history)
            log('写入完毕')

            return result,ms
        
        else:
            log(f'状态码错误 {result}','Warn')
            return f"api错误: {result}",0
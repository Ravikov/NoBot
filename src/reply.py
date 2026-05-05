import time
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
                history['history'] = [{"role": "user","content": "对话格式举例"},{"role": "assistant","content": "在在在#我刚在玩游戏#你呢 你干啥呢"}]
                history['memory'] = [{"role": "system","content": ""}]
                history['turns'] = 0
                save_history(history)
                log('清除记忆')
                return ['清除记忆成功'],0
            case 'memory':
                log('记忆总结...')
                re,e = set_memory()
                if e:
                    return {'reply': re}
                else:
                    return {'reply': re}
            case _:
                log('未知指令,本次输入略过')
                return ['未知的指令'],0
    else:
        log('调用辅助模型判断联网功能...')
        or_search = sec_llm(
            0,
            [{'role': 'system','content': mes}]+
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
        log(str(orgin_result))
        if state == 200:
            # 输出清洗
            text = ''
            for i in result:
                if i in config['txt_wash']:
                    pass
                elif i == '，':
                    text = text+' '
                else:
                    text = text+i
            result = text

            # 拆分多段消息
            re = []
            txt = ''
            for t in result:
                if t != '#':
                    txt = txt + t
                else:
                    re.append(txt)
                    txt = ''
            re.append(txt)
            result = re
            log(type(result))

            log(f'状态正确,提交回复: {result}')

            history = load_history()
            if history.get('turns') >= config.get('max_history_turns') - 1:
                log('需要进行记忆总结,正在调用api')
                set_memory()
            else:
                pass

            log('写入记忆...')
            history = load_history()
            history['history'].append({"role": "user", "content": f"[发送本条消息的时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]"+mes})
            # 将列表合并为字符串
            txt = ''
            n = 0
            for t in result:
                if n == 0:
                    txt = txt + t
                    n+=1
                else:
                    txt = txt + '#' + t
            history['history'].append({"role": "assistant", "content": txt})
            history['turns'] = history.get('turns') + 1
            save_history(history)
            log('写入完毕')

            return result,ms
        
        else:
            log(f'状态码错误 {result}','Warn')
            return f"api错误: {result}",0
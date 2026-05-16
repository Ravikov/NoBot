import time
from src.common import load_history,save_history,config
from src.memory import set_memory
from src.touch_llm import *
from debug.log import log

def reply(mes):
    """
    处理消息并生成回复
    返回: ({'type': int, 'msg': list}, ms)
      type=1: 正常文本回复
      type=2: 错误消息
    """
    # 判断消息类型
    if mes['type'] == 1:
        msg = mes['msg']
    elif mes['type'] in [2,5]:
        media = mes['msg']
    else:
        log('消息为空')
        return {'type': 2, 'msg': ['消息异常']}, 0
        
    def text(msg):
        if config['or_search']:
            log('调用辅助模型判断联网功能...')
            or_search = sec_llm(
                0,
                [{'role': 'system','content': msg}]+
                config['or_search_prompt']
            )
            log(f'判断完毕,结果: {or_search}')
        else:
            or_search = '0'
        if or_search == '1':
            log('调用联网搜索模型...')
            return search_api(msg)
        elif or_search == '0':
            log('调用主模型api...')
            return fst_llm(msg)
        else:
            log('辅助模型输出错误')
            return {'type': 2, 'msg': ['辅助模型判断异常']}, 0

    if mes['type'] == 1:
        if msg[0] == '/':
            match msg[1:]:
                case 'rememory':
                    history = load_history()
                    history['history'] = [{"role": "user","content": "对话格式举例"},{"role": "assistant","content": "在在在#我刚在玩游戏#你呢 你干啥呢"}]
                    history['memory'] = [{"role": "system","content": ""}]
                    history['turns'] = 0
                    save_history(history)
                    log('清除记忆')
                    return {'type': 1, 'msg': ['清除记忆成功']}, 0
                case 'memory':
                    log('记忆总结...')
                    re, e = set_memory()
                    return re, 0
                case _:
                    log('未知指令,本次输入略过')
                    return {'type': 1, 'msg': ['未知的指令']}, 0
        else:
            result,state,ms,orgin_result = text(msg)
    elif mes['type'] in [2,5]:
        if mes['type'] == 2:
            mes_type = '图片'
        elif mes['type'] == 5:
            mes_type = '视频'
        log(f'收到{mes_type},调用模型理解')
        result,state,ms,orgin_result = multimodal(mes['type'],media)
        media_dscrb = result
        log(f'{mes_type}描述:{media_dscrb}')
        result,state,ms,orgin_result = text(f'<{mes_type}消息(由多模态AI描述)>{result}')

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
                if txt != '':
                    re.append(txt)
                    txt = ''
        re.append(txt)
        result = re

        log(f'状态正确,提交回复: {result}')

        history = load_history()
        if history.get('turns') >= config.get('max_history_turns') - 1:
            log('需要进行记忆总结,正在调用api')
            set_memory()
        else:
            pass

        log('写入记忆...')
        history = load_history()
        if mes['type'] in [2,5]:
            msg = f'<{mes_type}(描述由AI生成)>{media_dscrb}'
        history['history'].append({"role": "user", "content": f"[发送本条消息的时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]"+msg})
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

        return {'type': 1, 'msg': result}, ms
    
    else:
        log(f'状态码错误 {state}','Warn')
        return {'type': 2, 'msg': [f'api错误: {state}']}, 0

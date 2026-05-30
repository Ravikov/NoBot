import time
from nobot.src.common import load_history,save_history,load_config
from nobot.src.core.mem.memory import set_memory
from nobot.src.core.get_reply.touch_llm import *
from debug.log import log

def reply(msg):
    """
    处理消息并生成回复
    输入: msg = {'type': int, 'msg': list/string, 'media': list/string}
      type=1: 文本消息, msg为字符串或字符串列表
      type=2: 图片消息, msg为图片的base64字符串
      type=5: 视频消息, msg为视频的base64字符串
      type=9: 消息列表, msg为字符串列表, media为对应的多媒体消息列表(格式同上)
    返回: ({'type': int, 'msg': list}, ms)
      type=1: 正常文本回复
      type=0: 错误消息
    """

    config = load_config()

    # 判断消息类型
    debug_log(f'reply函数输入: {msg}')
    if msg['type'] == 1:
        msgtxt = msg['msg']
    elif msg['type'] in [2,3,5]:
        media = msg['msg']
    elif msg['type'] == 9:
        msgtxt = msg['msg']
        media = msg['media']
    else:
        log('消息类型异常')
        return {'type': 0, 'msg': ['消息异常'], 'delay': 0}
        
    def txt_wash(text,wash = config['txt_wash']):
        # 输出清洗
        t = ''
        for i in text:
            if i in wash:
                pass
            elif i == '，':
                t = t+' '
            else:
                t = t+i
        return t
    def text(msgtxt):
        if config['or_search']:
            log('调用辅助模型判断联网功能...')
            or_search = sec_llm(
                0,
                [{'role': 'system','content': msgtxt}]+
                config['or_search_prompt']
            )
            log(f'判断完毕,结果: {or_search}')
        else:
            or_search = '0'
        if or_search == '1':
            log('调用联网搜索模型...')
            return search_api(msgtxt)
        elif or_search == '0':
            log('调用主模型api...')
            return fst_llm(msgtxt)
        else:
            log('辅助模型输出错误')
            return {'type': 0, 'msg': ['辅助模型判断异常'], 'delay': 0}
        
    def media_reply(tpe,media):
        result,state,ms,orgin_result = multimodal(tpe,media)
        media_dscrb = result
        media_dscrb_log = txt_wash(media_dscrb,wash=["。","，","！","?","\n"])
        log(f'{msg_type_desc}描述:{media_dscrb_log}')
        return media_dscrb

    if msg['type'] == 1:
        if msgtxt[0] == '/':
            match msgtxt[1:]:
                case 'rememory':
                    history = load_history()
                    history['history'] = [{"role": "user","content": "对话格式举例"},{"role": "assistant","content": "在在在#我刚在玩游戏#你呢 你干啥呢"}]
                    history['memory'] = [{"role": "system","content": ""}]
                    history['turns'] = 0
                    save_history(history)
                    log('清除记忆')
                    return {'type': 1, 'msg': ['清除记忆成功'], 'delay': 0}
                case 'memory':
                    log('记忆总结...')
                    re = set_memory()
                    return re
                case _:
                    log('未知指令,本次输入略过')
                    return {'type': 1, 'msg': ['未知的指令'], 'delay': 0}
        else:
            result = text(msgtxt)
    elif msg['type'] in [2,5]:
        if msg['type'] == 2:
            msg_type_desc = '图片'
        elif msg['type'] == 5:
            msg_type_desc = '视频'
        log(f'收到{msg_type_desc},调用模型理解')
        media_dscrb= media_reply(msg['type'],msg['media'])
        result,state,ms,orgin_result = text(f'<{msg_type_desc}消息(由多模态AI描述)>{media_dscrb}')
    elif msg['type'] == 9:
        log('收到消息列表,调用模型处理...')
        n_media = 1
        for m in msg['media']:
            if m['type'] == 2:
                msg_type_desc = '图片'
            elif m['type'] == 5:
                msg_type_desc = '视频'
            log(f'处理{msg_type_desc}消息{n_media}...')
            media_dscrb = media_reply(m['type'],m['media'])
            msgtxt[msgtxt.index(f'<{msg_type_desc}消息{n_media}>')] = f'<{msg_type_desc}消息{n_media}(由多模态AI描述)>{media_dscrb}'
            n_media += 1
        msgtxt = '#'.join(msgtxt)
        result,state,ms,orgin_result = text(str(msg))

    log('状态码审查...')
    # log(str(orgin_result))
    if state == 200:
        result = txt_wash(result)

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
        if msg['type'] in [2,5]:
            msgtxt = f'<{msg_type_desc}(描述由AI生成)>{media_dscrb}'
        history['history'].append({"role": "user", "content": f"[发送本条消息的时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]"+msgtxt})
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

        return {'type': 1, 'msg': result, 'delay': ms}
    
    else:
        log(f'状态码错误 {state}','Warn')
        return {'type': 0, 'msg': [f'api错误: {state}'], 'delay': 0}

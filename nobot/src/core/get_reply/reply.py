import time
from nobot.src.common import load_history, save_history, load_config
from nobot.src.core.mem.memory import set_memory
from nobot.src.core.get_reply.touch_llm import *
from debug.log import log


class ReplyHandler:
    """处理消息并生成回复"""

    def __init__(self):
        self.config = load_config()

    # ---- 内部工具 ----
    def _txt_wash(self, text, wash=None):
        """清洗回复文本"""
        if wash is None:
            wash = self.config['txt_wash']
        t = ''
        for i in text:
            if i in wash:
                pass
            elif i == '，':
                t = t + ' '
            else:
                t = t + i
        return t

    def _text(self, msgtxt):
        """文本 → 调用主模型或联网搜索"""
        if self.config['or_search']:
            log('调用辅助模型判断联网功能...')
            or_search = sec_llm(
                0,
                [{'role': 'system', 'content': msgtxt}] +
                self.config['or_search_prompt']
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
            return None, 0, 0, None

    def _media_reply(self, tpe, media, type_desc):
        """多媒体 → 调用多模态模型理解"""
        result, state, ms, orgin_result = multimodal(tpe, media)
        if result is None:
            log(f'{type_desc}理解失败', 'Warn')
            return ''
        media_dscrb = result
        media_dscrb_log = self._txt_wash(media_dscrb, wash=["。", "，", "！", "?", "\n"])
        log(f'{type_desc}描述:{media_dscrb_log}')
        return media_dscrb

    # ---- 主入口 ----
    def handle(self, msg):
        """
        处理消息并生成回复
        输入: msg = {'type': int, 'msg': list/string, 'media': list/string}
        返回: {'type': int, 'msg': list, 'delay': float}
        """
        debug_log(f'reply函数输入: {msg}')

        # ---- 消息类型分发 ----
        if msg['type'] == 1:
            msgtxt = msg['msg']
            media = None
        elif msg['type'] in [2, 3, 5]:
            msgtxt = None
            media = msg['msg']
        elif msg['type'] == 9:
            msgtxt = msg['msg']
            media = msg['media']
        else:
            log('消息类型异常')
            return {'type': 0, 'msg': ['消息异常'], 'delay': 0}

        # ---- 按类型处理 ----
        if msg['type'] == 1:
            # 文本消息
            if msgtxt[0] == '/':
                cmd = msgtxt[1:]
                if cmd == 'rememory':
                    history = load_history()
                    history['history'] = [{"role": "user", "content": "对话格式举例"}, {"role": "assistant", "content": "在在在#我刚在玩游戏#你呢 你干啥呢"}]
                    history['memory'] = [{"role": "system", "content": ""}]
                    history['turns'] = 0
                    save_history(history)
                    log('清除记忆')
                    return {'type': 1, 'msg': ['清除记忆成功'], 'delay': 0}
                elif cmd == 'memory':
                    log('记忆总结...')
                    return set_memory()
                else:
                    log('未知指令,本次输入略过')
                    return {'type': 1, 'msg': ['未知的指令'], 'delay': 0}
            else:
                result, state, ms, orgin_result = self._text(msgtxt)

        elif msg['type'] in [2, 5]:
            # 多媒体消息
            type_desc = '图片' if msg['type'] == 2 else '视频'
            log(f'收到{type_desc},调用模型理解')
            media_dscrb = self._media_reply(msg['type'], msg['media'], type_desc)
            result, state, ms, orgin_result = self._text(
                f'<{type_desc}消息(由多模态AI描述)>{media_dscrb}'
            )

        elif msg['type'] == 9:
            # 消息列表
            log('收到消息列表,调用模型处理...')
            n_media = 1
            for m in msg['media']:
                type_desc = '图片' if m['type'] == 2 else '视频'
                log(f'处理{type_desc}消息{n_media}...')
                media_dscrb = self._media_reply(m['type'], m['media'], type_desc)
                placeholder = f'<{type_desc}消息{n_media}>'
                msgtxt[msgtxt.index(placeholder)] = \
                    f'{placeholder}(由多模态AI描述)>{media_dscrb}'
                n_media += 1
            msgtxt = '#'.join(msgtxt)
            result, state, ms, orgin_result = self._text(str(msg))

        # ---- 后处理：清洗 + 拆分 ----
        result = self._txt_wash(result)

        re_list = []
        txt = ''
        for t in result:
            if t != '#':
                txt = txt + t
            else:
                if txt != '':
                    re_list.append(txt)
                    txt = ''
        re_list.append(txt)
        result = re_list

        log(f'状态正确,提交回复: {result}')

        # ---- 记忆管理 ----
        history = load_history()
        if history.get('turns', 0) >= self.config.get('max_history_turns', 20) - 1:
            log('需要进行记忆总结,正在调用api')
            set_memory()

        log('写入记忆...')
        history = load_history()
        if msg['type'] in [2, 5]:
            user_msg = f'<{type_desc}(描述由AI生成)>{media_dscrb}'
        else:
            user_msg = msgtxt
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        history['history'].append({
            "role": "user",
            "content": f"[发送本条消息的时间:{timestamp}]" + str(user_msg)
        })
        # 将多条回复用 # 合并
        txt = ''
        for i, t in enumerate(result):
            if i == 0:
                txt = t
            else:
                txt = txt + '#' + t
        history['history'].append({"role": "assistant", "content": txt})
        history['turns'] = history.get('turns', 0) + 1
        save_history(history)
        log('写入完毕')

        return {'type': 1, 'msg': result, 'delay': ms}


# ---- 保持原有函数接口，旧代码调用 reply(msg) 仍然可用 ----
_handler = None

def reply(msg):
    global _handler
    if _handler is None:
        _handler = ReplyHandler()
    return _handler.handle(msg)

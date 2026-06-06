import time
from nobot.src.common import load_history, save_history, load_config
from nobot.src.core.mem.memory import set_memory
from nobot.src.core.get_reply.touch_llm import *
from debug.log import *


class Reply:
    """接收标准格式消息字典 生成回复"""

    def __init__(self, msgdict):
        """
            标准输入格式:
            {
            'msg': []
            'type': 1/2/5/9
            'media': [{'type': ,'media': }]
            }
            标准输出格式:
            {
            'msg': []
            'type': 1
            'delay': ms
            }
        """
        debug_log(f'消息输入Reply:{msgdict}')
        self.msgdict = msgdict
        self.config  = load_config()
        self.memory  = load_history()
        self.llm_msg = {}
        self.touch_result = {}

    def media(self):
        n = 1
        for i in self.msgdict['media']:
            log('调用视觉模型...')
            type_desc = '图片' if i['type'] == 2 else '视频'
            toucher = TouchLLM(
                msg=i['media'],
                llm='multimodalAPI',
                tpe=i['type']
                )
            toucher.touch()
            self.touch_result = toucher.result
            self.touch_result['msg'] = self.txt_wash(self.touch_result['msg'],wash=["。", "，", "！", "?", "\n"])
            if self.msgdict['type'] == 9:
                placehoder = f'<{type_desc}消息{n}>'
                self.msgdict['msg'][self.msgdict['msg'].index(placehoder)] = f'<{type_desc}消息(描述由多模态AI提供)>{self.touch_result["msg"]}'
                n+=1
            else:
                self.msgdict['msg'] = f'<{type_desc}消息(描述由多模态AI提供)>{self.touch_result["msg"]}'

    def text(self):
        match self.msgdict['msg']:

            case '/rememory':
                log('清除记忆')
                self.memory['history'] = [
                    {"role": "user", "content": "对话格式举例,非用户消息与上下文,回复格式请遵从于此"}, 
                    {"role": "assistant", "content": "在在在#我刚在玩游戏#你呢 你干啥呢"}
                    ]
                self.memory['turns'] = 0
                save_history(self.memory)
                self.llm_msg = {
                    'msg': '清除记忆成功',
                    'type': 1,
                    'delay': 0
                    }

            case '/memory':
                log('总结记忆...')
                self.touch_result = set_memory()
                self.llm_msg = {
                    'msg': self.txt_wash(self.touch_result['msg']),
                    'type': self.touch_result['type'],
                    'delay': self.touch_result['delay']
                    }

            case _:
                if self.msgdict['type'] == 9:
                    self.msgdict['msg'] = '#'.join(self.msgdict['msg'])
                log(f'调用辅助模型判断联网...')
                toucher = TouchLLM(
                    msg=None,
                    llm='secAPI',
                    sysmsg=(
                        self.config['or_search_prompt']
                        + [{'role':'user','content':f"判断本消息:{self.msgdict['msg']}"}]
                        )
                    )
                toucher.touch()
                log(f'判断完毕:{toucher.result["msg"]}')
                if toucher.result['msg'] == '0':
                    toucher.llm = 'API'
                    toucher.usrmsg = self.msgdict['msg']
                    toucher.touch()
                else:
                    toucher.search = True
                    toucher.llm = 'searchAPI'
                    toucher.usrmsg = self.msgdict['msg']
                    toucher.touch()
                
                self.touch_result = toucher.result
        
        
    def reply(self):
        # 类型判断
        match self.msgdict['type']:
            case 1:
                log(f'收到文本消息:{self.msgdict["msg"]}')
                self.text()
            case 2 | 5 | 9:
                log(f"收到消息:{self.msgdict['msg']},type:{self.msgdict['type']}")
                self.media()
                self.text()
            case _:
                log('消息类型未匹配!')
                return {}

        if self.msgdict['msg'][0] != '/':
            self.touch_result['msg'] = self.txt_wash(self.touch_result['msg'])

            msg_list = []
            txt = ''
            for t in self.touch_result['msg']:
                if t != '#':
                    txt = txt + t
                else:
                    if txt != '':
                        msg_list.append(txt)
                        txt = ''
            msg_list.append(txt)
            debug_log(msg_list)
            self.touch_result['msg'] = msg_list

            self.llm_msg = {
                'msg': self.touch_result['msg'],
                'type': self.touch_result['type'],
                'delay': self.touch_result['delay']
                }
            
            self.touch_result['msg'] = '#'.join(self.touch_result['msg'])
            self.memory['history']+=[
                {'role':'user','content':self.msgdict['msg']},
                {'role':'assistant','content':self.touch_result['msg']}
                ]

            if self.memory['turns'] >= self.config['max_history_turns']:
                log('进行记忆总结...')
                set_memory()


    def txt_wash(self, txt, wash=None):
        """清洗回复文本"""
        if wash is None:
            wash = self.config['txt_wash']
        t = ''
        for i in txt:
            if i in wash:
                pass
            elif i == '，' and self.config['wash_comma']:
                t = t + ' '
            else:
                t = t + i
        return t
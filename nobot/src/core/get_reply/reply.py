import time
from nobot.src.common import load_history, save_history, load_config, DEFAULT_MEMORY, DEFAULT_LONGHISTORY, save_longhistory
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
        self.note    = []

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
                save_history(DEFAULT_MEMORY)
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
                
            case '/rehistory':
                log('清除长上下文保存')
                save_longhistory(DEFAULT_LONGHISTORY)
                self.llm_msg = {
                    'msg': '清除长上下文成功',
                    'type': 1,
                    'delay': 0
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
                if toucher.result['delay'] != -1 and toucher.result['msg'] == '1':
                    toucher.search = True
                    toucher.llm = 'searchAPI'
                    toucher.usrmsg = self.msgdict['msg']
                    toucher.touch()
                else:
                    if toucher.result['delay'] == -1:
                        self.note.append(f"""本次回答中辅助模型出现了错误,详情如下:
---------------\n{toucher.result['msg']}""")
                    toucher.llm = 'API'
                    toucher.usrmsg = self.msgdict['msg']
                    toucher.touch()
                
                self.touch_result = toucher.result
        
        
    def reply(self):
        # funny-复读鸡
        if self.config['repeat']:
            self.llm_msg ={
                'msg': self.msgdict['msg'],
                'type': 1,
                'delay': 0
                }
            return
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
                self.llm_msg = {
                    'msg': f"您发送的消息,其类型: {self.msgdict['type']},可能是当前未支持的消息类型",
                    'type': 1,
                    'delay': -1
                    }
                return

        if self.msgdict['msg'][0] != '/':
            self.touch_result['msg'] = self.txt_wash(self.touch_result['msg'])

            msg_list = self.touch_result['msg'].split('#')
            debug_log(msg_list)
            self.touch_result['msg'] = msg_list

            self.llm_msg = {
                'msg': self.touch_result['msg']+self.note,
                'type': self.touch_result['type'],
                'delay': self.touch_result['delay']
                }
            self.note = []
            
            self.touch_result['msg'] = '#'.join(self.touch_result['msg'])
            self.memory['history']+=[
                {'role':'user','content':f"本条消息发送时间{time.strftime('%Y-%m-%d %H:%M', time.localtime())}"+self.msgdict['msg']},
                {'role':'assistant','content':self.touch_result['msg']}
                ]
            self.memory['turns'] += 1
            save_history(self.memory)

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
import time
from nobot.src.common import *
from nobot.src.core.mem.memory import set_memory
from nobot.src.core.llm.touch_llm import *
from debug.log import *

from nobot.user.user import usrobj


class Reply:
    """接收标准格式消息字典 生成回复"""

    def __init__(self, msgdict):
        """
            标准输入格式:
            {
            'msg': []
            'type': 1/2/5/9/100
            'media': [{'type': ,'media': }]
            }
            esp32通讯格式:
            {
            'msg':文本内容
            'type':消息类型, 1日常对话, 0首次连接通讯
            }
            标准输出格式:
            {
            'msg': []或{}
            'type': 1
            'delay': ms
            }
        """
        # debug_log 截断 media 避免日志膨胀
        log_msgdict = {k: v for k, v in msgdict.items()}
        if isinstance(log_msgdict.get('media'), list):
            log_msgdict['media'] = [{'type': m['type'], 'media': f'<base64 {len(m["media"])} chars>'} for m in log_msgdict['media']]
        debug_log(f'消息输入Reply:{log_msgdict}')
        self.msgdict = msgdict
        self.config  = load_config()
        self.memory  = load_history()
        self.llm_msg = {} #最终输出(给前端)
        self.touch_result = {} #请求器调用结果
        self.note    = []
        self.esp_result = {'msg':""} #给esp32的输出

    def media(self):
        n = 1
        for i in self.msgdict['media']:
            log(f'调用视觉模型...')
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
    
    def esp32(self):
        if self.msgdict['type'] == 100:
            usrobj.action = self.msgdict['msg'] # 首次连接获取动作列表
            with open(CONFIG_FILE.parent/'actionAndHardware.txt', 'w', encoding='utf-8') as f:
                f.write(usrobj.action)
        elif self.msgdict['type'] in [101,105]:
            toucher = TouchLLM(
                msg=self.msgdict['msg'],
                llm='API',
                tpe=101,
                action_dscrb=usrobj.action
                )
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
            case 100 | 101:
                log('收到来自esp32的消息')
                self.esp32()
                if self.msgdict['type'] == 100:
                    self.llm_msg = {'msg':''}
                    return
            case 105:
                log('收到来自IM的esp32控制消息')
                self.media()
                self.text()
                self.esp32()
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
            debug_log(f"from reply: msg_list={msg_list}")
            msg_forUsr_list = ''
            if self.msgdict['type'] == 105:
                debug_log(f"from reply: self.touch_result={self.touch_result}")
                # time.sleep(100)
                data = []
                for i in msg_list:
                    msg = json.loads(i)
                    data.append(msg)
                msg_list = data
                msg = msg_list[0]['msg']
                debug_log(f"将向用户发送的消息: {msg}")
                msg_forUsr_list = msg.split('$')
            else:
                msg_forUsr_list = msg_list

            if self.msgdict['type'] in [100,101,105]:
                self.esp_result = {  
                    'msg': msg_list,
                    'type': self.touch_result['type'],
                    'delay': self.touch_result['delay']
                    }

            self.llm_msg = {  #这是给用户看的消息
                'msg': list(msg_forUsr_list)+self.note,
                'type': self.touch_result['type'],
                'delay': self.touch_result['delay']
                }
            
            self.note = []

            memory_msg = self.touch_result['msg']

            self.memory['history']+=[
                {'role':'user','content':f"本条消息发送时间{time.strftime('%Y-%m-%d %H:%M', time.localtime())}>>"+self.msgdict['msg']},
                {'role':'assistant','content':memory_msg}
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
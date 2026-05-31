import time
from nobot.src.common import load_config
from debug.log import *
from message.clawbot.wechatmsg import WechatBotMessage
from nobot.src.core.get_reply.touch_llm import sec_llm
from nobot.src.common import load_history

class Witimer(WechatBotMessage): #传入消息handle对象 获取等待时间

    def __init__(self, msgobj, process_now):
        super().__init__()
        self.msgtime = time.time()
        self.msgtext = msgobj.msgtext
        self.msgtype = msgobj.msgtype
        self.msglist    = msgobj.msglist
        self.medialist   = msgobj.medialist
        self.media       = msgobj.media
        self.msgnum      = msgobj.msgnum

        self.botconfig = load_config() #等待器特有属性
        self.process_now = process_now
        self.timeout = 35

    def set_msglist(self):
        log(str(self.msglist))
        if not self.msglist == []:
            log(f'提交消息接收,共{self.msgnum}条')
            if len(self.msglist) == 1 and self.medialist == []:
                self.msgtext = self.msglist[0] # 单条文本消息
                self.msgtype = 1
            elif len(self.msglist) == 1 and self.medialist != []:
                self.msgtext = self.msglist[0]
                self.msgtype = self.medialist[0]['type'] # 单条媒体消息
                self.media   = self.medialist[0]['media']
            else:
                self.msgtext = self.msglist
                self.media = self.medialist
                self.msgtype = 9 # 队列消息
            self.userid = self.config['userid']
            log(f'最终消息列表: {self.msgtext}')
            

    def set_waitime(self):
        
        if not self.process_now:
            history = load_history()
            self.msgtime = time.time()
            debug_log(f'消息时间戳 {self.msgtime}')
            self.msgnum += 1
            if self.botconfig['llm_decide_wait']:
                log('调用模型判断等待...')
                waitime = sec_llm(
                    0.5,
                    [{
                        'role':'system',
                        'content':"""判断本条消息需要等待下一条输入的时间(1~50),无论如何都要给以等待时间,
                                    仅回复整数,不能包含任何其他内容,你需要推测用户行为来判断等待时间,例如拍摄照片要多等一会，
                                    如:用户输入了"我拍了一张照片",你可以判断用户可能在拍照并等待照片上传,
                                    这时你可以回复几十秒来让程序多等待一会(一般大于30),照片上传完成后再继续处理消息.
                                    用户输入了'我在想一个问题',你可以判断用户可能在思考,
                                    这时你也可以让程序多等待一会(建议大于20)再处理消息.
                                    用户输入'等一下','稍等','等等'这一类时,也要稍微增加等待时间(建议5~15)来提升用户体验.
                                    其他诸如'对了','我突然想起来',''我还有件事'等可能一切引发用户连续输入的消息,适当增加等待时间来提升用户体验.
                                    禁止回复0和负数,要根据用户的行为来判断合理的等待时间,
                                    如果用户某条消息需要等待他发下一条,你回复了1或者2,程序就会马上处理消息,这会导致用户还没想好就被打断,
                                    但是过长的等待又会造成用户干等,体验下降,所以多数一般性问题建议在5~15为最佳,
                                    所以请用合理的等待时间提升用户体验.
                                    不要太小也不要太大,合理判断!!!"""
                    }]+
                    [{
                        'role':'system',
                        'content':f'<过往消息列表>{(self.msglist[:-1])}<本条消息内容>{self.msgtext}'
                    }]+
                    history['history']+
                    history['memory']+
                    [{'role':'user','content':''}]
                )
                log(f'判断结果: {waitime}')
                try:
                    waitime = int(waitime)
                    log(f'等待{waitime}秒')
                except:
                    log('返回有误')
                    waitime = 0
            else:
                waitime = 0
            timeout = self.botconfig['wait'] + waitime
            if timeout < self.botconfig['wait']:
                timeout = self.botconfig['wait']
            elif timeout < 0:
                timeout = 0
            log(f'设置下一轮轮询超时时间为{timeout}秒')
            self.timeout = timeout
            log(self.msglist)
        
        else:
            self.set_msglist()
            return 1
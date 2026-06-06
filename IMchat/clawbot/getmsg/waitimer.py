from nobot.src.common import load_config
from debug.log import *
from nobot.src.core.get_reply.touch_llm import sec_llm
from nobot.src.common import load_history

class Waitimer(): #传入消息handle对象 获取等待时间

    def __init__(self, msgobj):
        super().__init__()
        self.msgtext = msgobj.msgtext
        self.msgtype = msgobj.msgtype
        self.msglist = msgobj.msglist
        self.msgnum  = msgobj.msgnum
        self.msgtime = msgobj.msgtime

        self.botconfig = load_config() #等待器特有属性
        self.timeout = 35

    def set_waitime(self):
        
        history = load_history()
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
                                如果收到的消息结构类似[time:整数],则直接回复这个整数
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
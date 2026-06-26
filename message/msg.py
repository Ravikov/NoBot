from debug.log import *
import time
import traceback
import queue
from nobot.src.core.reply.reply import Reply

# 消息类

# 父类
class Message:
    """通用消息协议,包含msgtype,msgtext,fromuser(bot/wechatbot),media,msglist,medialist"""
    
    def __init__(self,msgtype=None, msgtext=None, fromusr=None, media=None):
        self.msgtype = msgtype #消息格式,1文本,2图片,5视频,9队列
        self.msgtext = msgtext #消息文本内容,列表/字符串
        self.fromusr = fromusr #消息来源,bot/wechatbot
        self.media = media #多媒体消息,base64字符串/列表
        self.msglist = [] #消息列表
        self.medialist = [] #多媒体列表
        self.msgtime = time.time() #消息时间戳
        self.msgnum = 0 #消息数量

# 子类 reply函数输出消息 传入reply返回的字典构造Message对象
class ReplyOut(Message):
    def __init__(self, outdict):
        super().__init__(msgtype=outdict['type'], msgtext=outdict['msg'], fromusr='bot', media=None)

    # 获取当前输出消息信息
    def get_info(self):
        return {
            'type': self.msgtype,
            'msg': self.msgtext,
            'fromusr': self.fromusr,
            'media': self.media
        }


msg_queue = queue.Queue()
# 子类 reply函数输入消息 以消息对象构建reply输入字典
class ReplyIn(Message):
    def __init__(self, msgdict):
        super().__init__(msgtype=msgdict['type'],
                         msgtext=msgdict['msg'],
                         fromusr=msgdict['fromusr'],
                         media=msgdict['media'])

    def get_reply(self):
        global msg_queue
        
        try:
            replyer = Reply({'type': self.msgtype, 'msg': self.msgtext, 'media': self.media})
            replyer.reply()
            if self.msgtype == 105:
                msg_queue.put(replyer)
                debug_log(f'from ReplyIn.get_reply: msg_queue.put size:{msg_queue.qsize()}')
            llm_msg = replyer.llm_msg
        except Exception as e:
            log(f'发生错误: {traceback.format_exc()}')
            traceback_msg = traceback.format_exc()
            llm_msg = {
                'msg': [f"""发生未能处理的错误,可以尝试重新发送消息,但不保证错误不会再次触发...
---------------
Traceback报错:\n{traceback_msg}
---------------
str(e):{str(e)}
repr(e):{repr(e)}""",],
                'type': -1,
                'media': None
                }
        return ReplyOut(llm_msg) #返回回复消息对象
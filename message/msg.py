from debug.log import log
import time
from nobot.src.core.get_reply.reply import Reply

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


# 子类 reply函数输入消息 以消息对象构建reply输入字典
class ReplyIn(Message):
    def __init__(self, msgobj):
        super().__init__(msgobj.msgtype, msgobj.msgtext, fromusr=msgobj.fromusr, media=msgobj.media)

    def get_reply(self):
        replyer = Reply({'type': self.msgtype, 'msg': self.msgtext, 'media': self.media})
        replyer.reply()
        return ReplyOut(replyer.llm_msg) #返回回复消息对象
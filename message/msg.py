from debug.log import log
from nobot.src.core.get_reply.reply import reply

# 消息类

# 父类
class Message:
    
    def __init__(self,msgtype, msgtext, fromusr, media=None):
        self.msgtype = msgtype #消息格式,1文本,2图片,5视频,9队列
        self.msgtext = msgtext #消息文本内容,列表/字符串
        self.fromusr = fromusr #消息来源,bot/wechatbot
        self.media = media #多媒体消息,base64字符串/列表

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


# 子类 reply函数输入消息
class ReplyIn(Message):
    def __init__(self, msgtype, msgtext, media=None):
        super().__init__(msgtype, msgtext, fromusr='user', media=media)

    def get_reply(self):
        return ReplyOut(reply({'type': self.msgtype, 'msg': self.msgtext, 'media': self.media})) #返回回复消息对象




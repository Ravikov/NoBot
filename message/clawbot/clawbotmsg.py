import uuid
from IMchat.clawbot.clawbot_common import random_wechat_uin
from message.msg import *
from IMchat.clawbot.clawbot_common import load_clawbot_config
from debug.log import *

from nobot.user.user import usrobj

# 子类/父类
class WechatBotMessage(Message): # 微信bot消息基础格式 基本通讯协议

    def __init__(self):
        super().__init__()
        self.fromusr = 'wechatbot'   # 不同于userid

        # 运行期属性（父类 Message 已初始化 msgtype/msgtext/media/msglist/medialist）
        self.msgtime = None
        self.context_token = None
        self.msgnum = 0

    def get_msg_reply(self):
        """将wechat消息交由reply处理"""
        if usrobj.type == 'chat':
            pass
        elif usrobj.type == 'esp32':
            debug_log("from clawbotMsg: usrobj.type=esp32")
            self.msgtype = 105  #esp32与chat组合消息处理类型
        msgdict = {
                'msg': self.msgtext,
                'type': self.msgtype,
                'media': self.media,
                'fromusr': self.fromusr
                }
        debug_log(msgdict)
        replyout = ReplyIn(msgdict).get_reply()
        replyout.context_token = self.context_token
        return replyout # ReplyOut消息对象(额外添加c_t属性)

# wechatbot用户信息
class WechatBotUsr:
    def __init__(self, userid, name, token):
        self.userid  = userid
        self.name    = name
        self.token   = token
        self.baseurl = 'https://ilinkai.weixin.qq.com'
        self.config = load_clawbot_config()
        self.client_id = self.config.get('client_id', str(uuid.uuid4()))
        self.uin = random_wechat_uin()
        
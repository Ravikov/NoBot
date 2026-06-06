import uuid
from IMchat.clawbot.clawbot_common import random_wechat_uin
from message.msg import Message
from IMchat.clawbot.clawbot_common import load_clawbot_config


# 子类/父类
class WechatBotMessage(Message): # 微信bot消息基础格式 基本通讯协议

    def __init__(self):
        super().__init__()
        self.fromusr = 'wechatbot'   # 不同于userid

        # 运行期属性（父类 Message 已初始化 msgtype/msgtext/media/msglist/medialist）
        self.msgtime = None
        self.context_token = None
        self.msgnum = 0

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
        
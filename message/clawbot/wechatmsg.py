import uuid
from IMchat.clawbot.wechat_common import random_wechat_uin
from message.msg import Message
from IMchat.clawbot.wechat_common import load_clawbot_config


# 子类/父类
class WechatBotMessage(Message): # 微信bot消息基础格式 基本通讯协议

    def __init__(self):
        super().__init__()
        self.fromusr = 'wechatbot'   # 不同于userid

        # 常量属性
        self.config    = load_clawbot_config()
        self.userid    = self.config.get('userid')
        self.token     = self.config.get('token')
        self.cursor    = self.config.get('cursor','')
        self.client_id = self.config.get('clientid',uuid.uuid4())
        self.baseurl   = 'https://ilinkai.weixin.qq.com'
        self.uin       = random_wechat_uin()

        # 运行期属性（父类 Message 已初始化 msgtype/msgtext/media/msglist/medialist）
        self.msgtime = None
        self.context_token = None
        self.msgnum = 1
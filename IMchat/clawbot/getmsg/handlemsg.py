from message.clawbot.wechatmsg import WechatBotMessage
from debug.log import *
from IMchat.clawbot.getmsg.mediagetter import MediaGetter

class Handle(WechatBotMessage):

    def __init__(self, updateobj, n_start=1):
        super().__init__()
        self.body = updateobj.body #getupdates响应体
        self.msgtext = updateobj.msgtext
        self.msgtype = updateobj.msgtype
        self.n_media     = n_start
        self.n            = 1
        self.process_now  = False

    def fetch(self):
        # 文本消息
        if self.msgtype == 1:
            self.msgtext = self.body['msgs'][0]['item_list'][0]['text_item']['text']
            log(f'消息监听get: {self.msgtext}, 类型: 1')
            self.msglist.append(self.msgtext)
            if self.msgtext[0] == '/':
                self.msglist = [self.msgtext]
                self.msgtext = None
                self.process_now = True

        # 图片/视频消息处理
        elif self.msgtype in [2,5]:
            type_desc = '图片' if self.msgtype == 2 else '视频'
            log(f'消息监听get: <{type_desc}消息>')
            # 先下载+解密媒体，再存入列表
            if self.msgtype == 2:
                aeskey = self.body['msgs'][0]['item_list'][0]['image_item']['aeskey']
                url = self.body['msgs'][0]['item_list'][0]['image_item']['media']['full_url']
                mediaget = MediaGetter(url, aeskey, ext='jpg')
                self.media = mediaget.getter()
            elif self.msgtype == 5:
                aeskey = self.body['msgs'][0]['item_list'][0]['video_item']['media']['aes_key']
                url = self.body['msgs'][0]['item_list'][0]['video_item']['media']['full_url']
                if not self.body['msgs'][0]['item_list'][0]['video_item'].get('media'):
                    log('视频媒体数据为空', 'Warn')
                    self.media = ''
                else:
                    mediaget = MediaGetter(url, aeskey)
                    self.media = mediaget.getter()
            self.msglist.append(f'<{type_desc}消息{self.n_media}>')
            self.medialist.append({'type': self.msgtype, 'media': self.media})
            self.msgtext = f'<{type_desc}消息>'
            self.n_media += 1
        else:
            log(f'未知消息类型: {self.msgtype}', 'Warn')

        self.context_token = self.body['msgs'][0]['context_token']
        get_msg = {
            'type': self.msgtype,
            'msg': self.msgtext,
            # 'to_user': self.config['userid'],
            # 'context_token': self.context_token,
            'media': self.media
        }
        debug_log(f'接收消息: {get_msg}')
        return get_msg
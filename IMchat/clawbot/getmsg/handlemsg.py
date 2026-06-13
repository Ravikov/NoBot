from message.clawbot.clawbotmsg import WechatBotMessage
from debug.log import *
from IMchat.clawbot.getmsg.mediagetter import MediaGetter

class Handle(WechatBotMessage):

    def __init__(self, usrobj):
        super().__init__()
        self.body    = None
        self.msgobj  = None
        self.usrobj  = usrobj
        self.n_media = 1
        self.n       = 1
        self.process_now  = False

    def fetch(self):
        self.msgtype = self.body['msgs'][0]['item_list'][0]['type']
        # 文本消息
        if self.msgtype == 1:
            self.msgobj.msgtext = self.body['msgs'][0]['item_list'][0]['text_item']['text']
            log(f'消息监听get: {self.msgobj.msgtext}, 类型: 1')
            self.msgobj.msglist.append(self.msgobj.msgtext)
            if self.msgobj.msgtext[0] == '/':
                self.msgobj.msglist = [self.msgobj.msgtext]
                self.msgobj.msgtext = None
                self.process_now = True

        # 图片/视频消息处理
        elif self.msgtype in [2,5]:
            type_desc = '图片' if self.msgtype == 2 else '视频'
            log(f'消息监听get: <{type_desc}消息>')
            # 先下载+解密媒体，再存入列表

            if self.msgtype == 2:
                aeskey = self.body['msgs'][0]['item_list'][0]['image_item']['aeskey']
                url = self.body['msgs'][0]['item_list'][0]['image_item']['media']['full_url']
                mediaget = MediaGetter(url, aeskey, self.usrobj, ext='jpg')
                self.media = mediaget.getter()

            elif self.msgtype == 5:
                aeskey = self.body['msgs'][0]['item_list'][0]['video_item']['media']['aes_key']
                url = self.body['msgs'][0]['item_list'][0]['video_item']['media']['full_url']
                if not self.body['msgs'][0]['item_list'][0]['video_item'].get('media'):
                    log('视频媒体数据为空', 'Warn')
                    self.media = ''
                else:
                    mediaget = MediaGetter(url, aeskey, self.usrobj, ext='mp4')
                    self.media = mediaget.getter()

            self.msgobj.msglist.append(f'<{type_desc}消息{self.n_media}>')
            self.msgobj.medialist.append({'type': self.msgtype, 'media': self.media})
            self.msgobj.msgtext = f'<{type_desc}消息>'
            self.n_media += 1

        else:
            log(f'未知消息类型: {self.msgtype}', 'Warn')

        self.msgobj.context_token = self.body['msgs'][0]['context_token']
        get_msg = {
            'type': self.msgobj.msgtype,
            'msg': self.msgobj.msgtext,
            # 'to_user': self.config['userid'],
            # 'context_token': self.context_token,
            'media': self.msgobj.media
        }
        # debug_log 截断 media 避免日志膨胀
        log_msg = get_msg.copy()
        if log_msg.get('media'):
            if isinstance(log_msg['media'], list):
                log_msg['media'] = [{'type': m['type'], 'media': f'<base64 {len(m["media"])} chars>'} for m in log_msg['media']]
            else:
                log_msg['media'] = f'<base64 {len(log_msg["media"])} chars>'
        debug_log(f'接收消息: {log_msg}')
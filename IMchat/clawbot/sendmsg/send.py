import threading
import time
import uuid
import requests
from debug.log import *
from IMchat.clawbot.clawbot_common import make_auth_headers
from .sendtyping import Typing
from message.clawbot.clawbotmsg import WechatBotMessage

class Sender():

    def __init__(self, msgobj, usrobj):
        self.typing        = Typing(msgobj, usrobj)
        self.userid        = usrobj.userid
        self.baseurl       = usrobj.baseurl
        self.token         = usrobj.token
        self.uin           = usrobj.uin

        self.context_token = msgobj.context_token
        self.msgtype       = msgobj.msgtype
        self.msgtext       = msgobj.msgtext
        self.media         = msgobj.media
        
    def send(self): #发送消息
        """发送回复消息（分条发送)"""

        log('获取ticket...')
        self.typing.get_config()
        n = 1
        if self.msgtype == 1:
            msgs = self.msgtext if isinstance(self.msgtext, list) else [self.msgtext]
            log(f'回复类型: text, 总条数: {len(msgs)}')
            for msg in msgs:
                if msg in [' ','']:
                    continue
                threading.Thread(target=self.typing.send_typing).start()
                time.sleep(0.5)
                text_token = self.context_token if n == 1 else ''
                data = {
                    "msg": {
                        "from_user_id": '',
                        "to_user_id": self.userid,
                        "context_token": text_token,
                        "message_type": 2,
                        "message_state": 2,
                        "client_id": str(uuid.uuid4()),
                        "item_list": [
                            {"type": 1, "text_item": {"text": msg}}
                        ],
                        'base_info': {"channel_version": "2.0.0"}
                    }
                }
                # log(str(data))
                log(f'发送第{n}条消息: {msg}')
                debug_log(f'请求发送消息 URL: {self.baseurl}/ilink/bot/sendmessage, headers: {make_auth_headers(self.token, self.uin)}, body: {data}')
                resp = requests.post(
                    f'{self.baseurl}/ilink/bot/sendmessage',
                    headers=make_auth_headers(self.token, self.uin),
                    json=data
                )
                time.sleep(2)
                debug_log(resp.text)
                if resp.status_code == 200 and resp.json() == {}:
                    log('本条消息发送成功')
                    n += 1
                else:
                    ret = resp.json().get('ret', '?')
                    log(f'发送失败, 状态码: {resp.status_code}, 返回码: {ret}')
                    return 1
        log('消息发送结束')
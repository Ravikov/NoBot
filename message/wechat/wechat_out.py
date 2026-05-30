import time
import requests
import threading
import uuid
from nobot.src.common import *
from nobot.src.core.get_reply.reply import reply
from IMchat.clawbot.wechat_common import random_wechat_uin, make_auth_headers
from message.msg import Message
from debug.log import log

# 子类 返回wechatbot消息 以ReplyOut对象构造Out对象
class WechatOut(Message):
    def __init__(self, msgobj, token, context_token, to_user):
        super().__init__(msgobj.msgtype, msgobj.msgtext, fromusr='wechatbot', media=None)
        self._token = token
        self._context_token = context_token
        self._to_user = to_user
        self.ticket = None
        self.baseurl = 'https://ilinkai.weixin.qq.com'
        self.uin = random_wechat_uin()

    # 获取 ticket 以申请打字状态
    def get_ticket(self):
        log('获取ticket...')
        debug_log(f'请求ticket URL: {self.baseurl}/ilink/bot/getconfig, headers: {make_auth_headers(self._token, self.uin)}')
        resp = requests.post(
            url=f'{self.baseurl}/ilink/bot/getconfig',
            headers=make_auth_headers(self._token, self.uin),
            json={
                'ilink_user_id': self._to_user,
                'context_token': self._context_token
            }
        )
        if resp.status_code == 200:
            return resp.json()['typing_ticket']

    def send_typing(self):
        log('申请打字状态...')
        debug_log(f'请求打字状态 URL: {self.baseurl}/ilink/bot/sendtyping, headers: {make_auth_headers(self._token, self.uin)}, body: {{"ilink_user_id": {self._to_user}, "typing_ticket": {self.ticket}}}')
        resp = requests.post(
            url=f'{self.baseurl}/ilink/bot/sendtyping',
            headers=make_auth_headers(self._token, self.uin),
            json={
                'ilink_user_id': self._to_user,
                'typing_ticket': self.ticket,
                'status': 1
            }
        )
        if resp.status_code == 200:
            log('打字状态申请成功')

    def send(self): #发送消息
        """发送回复消息（分条发送)"""
        self.ticket = self.get_ticket()
        n = 1
        if self.msgtype == 1:
            log(f'回复类型: text, 总条数: {len(self.msgtext)}')
            for msg in self.msgtext:
                if msg == ' ':
                    continue
                threading.Thread(target=self.send_typing).start()
                time.sleep(0.5)
                text_token = self._context_token if n == 1 else ''
                data = {
                    "msg": {
                        "from_user_id": '',
                        "to_user_id": self._to_user,
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
                debug_log(f'请求发送消息 URL: {self.baseurl}/ilink/bot/sendmessage, headers: {make_auth_headers(self._token, self.uin)}, body: {data}')
                resp = requests.post(
                    f'{self.baseurl}/ilink/bot/sendmessage',
                    headers=make_auth_headers(self._token, self.uin),
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
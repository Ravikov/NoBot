import requests
from debug.log import *
from IMchat.clawbot.clawbot_common import make_auth_headers,random_wechat_uin
from message.clawbot.clawbotmsg import WechatBotMessage

class Typing():

    def __init__(self, msgobj, usrobj):
        self.userid        = usrobj.userid
        self.uin           = usrobj.uin
        self.token         = usrobj.token
        self.baseurl       = usrobj.baseurl
        self.context_token = msgobj.context_token
        self.ticket        = None

    # 获取 ticket 以申请打字状态,亦可用于维持链接
    def get_config(self):
        debug_log(f'请求config URL: {self.baseurl}/ilink/bot/getconfig, headers: {make_auth_headers(self.token, self.uin)}')
        resp = requests.post(
            url=f'{self.baseurl}/ilink/bot/getconfig',
            headers=make_auth_headers(self.token, self.uin),
            json={
                'ilink_user_id': self.userid,
                'context_token': self.context_token
            }
        )
        if resp.status_code == 200:
            data = resp.json()
            self.ticket = data.get('typing_ticket')

    def send_typing(self):
        log('申请打字状态...')
        debug_log(f'请求打字状态 URL: {self.baseurl}/ilink/bot/sendtyping, headers: {make_auth_headers(self.token, self.uin)}, body: {{"ilink_user_id": {self.userid}, "typing_ticket": {self.ticket}}}')
        resp = requests.post(
            url=f'{self.baseurl}/ilink/bot/sendtyping',
            headers=make_auth_headers(self.token, self.uin),
            json={
                'ilink_user_id': self.userid,
                'typing_ticket': self.ticket,
                'status': 1
            }
        )
        if resp.status_code == 200:
            log('打字状态申请成功')
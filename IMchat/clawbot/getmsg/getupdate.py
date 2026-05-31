import requests
from message.clawbot.wechatmsg import WechatBotMessage
from IMchat.clawbot.wechat_common import make_auth_headers,save_clawbot_config
from debug.log import *

class GetUpdate(WechatBotMessage):

    def __init__(self, timeout):
        super().__init__()
        self.body = None
        self.timeout = timeout

    def getupdates(self):
        """长轮询获取一条消息
        返回: {'msg': ,'msg_type': ,'to_user': ,'context_token': } 或 None"""
        headers = make_auth_headers(self.token, self.uin)
        url = f'{self.baseurl}/ilink/bot/getupdates'
        state = 0  # 初始值, 防止未绑定
        try:
            data = {
                'get_updates_buf': self.cursor,
                'client_id': self.client_id,
                'base_info': {"channel_version": "2.0.0"}
            }
            debug_log(f'长轮询: {self.baseurl}/ilink/bot/getupdates, timeout={self.timeout}s')
            resp = requests.post(url=url, headers=headers, json=data, timeout=self.timeout)
            debug_log(resp.text)
            if resp.json().get('msgs'):
                state = resp.status_code
                self.body = resp.json()
                # 更新游标
                self.config['cursor'] = self.body.get('get_updates_buf')
                self.cursor = self.config['cursor']
                save_clawbot_config(self.config)
            else:
                return None
        except requests.exceptions.ReadTimeout:
            return None

        if state != 200:
            log(f'状态码错误: {state}')
            return None
        else:
            self.msgtype = self.body['msgs'][0]['item_list'][0]['type'] #消息类型获取
            self.msgtext = ''  # 非 None 标记，通知主循环有消息到达
            debug_log(f'接收消息类型: {self.msgtype}')
            return True

    # @property
    # def msg(self):
    #     return self.getupdates()
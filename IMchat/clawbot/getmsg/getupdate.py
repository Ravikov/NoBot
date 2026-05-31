import requests
from message.clawbot.wechatmsg import WechatBotMessage
from IMchat.clawbot.wechat_common import make_auth_headers,save_clawbot_config
from debug.log import *

class GetUpdate(WechatBotMessage):

    _poll_count = 0  # 类变量，所有实例共享轮询计数

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

        # 每 10 次轮询写一次普通日志，debug 模式每次都会写
        GetUpdate._poll_count += 1
        debug_log(f'长轮询: timeout={self.timeout}s')
        if GetUpdate._poll_count % 10 == 1:
            log(f'长轮询中, timeout={self.timeout}s')
        try:
            data = {
                'get_updates_buf': self.cursor,
                'client_id': self.client_id,
                'base_info': {"channel_version": "2.0.0"}
            }
            resp = requests.post(url=url, headers=headers, json=data, timeout=self.timeout)
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
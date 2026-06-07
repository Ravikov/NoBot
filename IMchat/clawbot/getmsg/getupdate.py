import requests
from nobot.src.common import *
from IMchat.clawbot.clawbot_common import make_auth_headers,save_clawbot_config
from debug.log import *

class GetUpdate():

    _poll_count = 0  # 类变量，所有实例共享轮询计数

    def __init__(self, usrobj):
        self.body = None
        self.timeout = 35
        self.usrobj = usrobj
        self.cursor = usrobj.config.get('cursor','')
        self.config = usrobj.config
        self.client_id = usrobj.client_id
        self.resp   = False # 标记消息获取情况

    def getupdates(self):
        """长轮询获取一条消息
        返回: {'msg': ,'msg_type': ,'to_user': ,'context_token': } 或 None"""
        headers = make_auth_headers(self.usrobj.token, self.usrobj.uin)
        url = f'{self.usrobj.baseurl}/ilink/bot/getupdates'
        state = 0  # 初始值, 防止未绑定

        # 每 10 次轮询写一次普通日志，debug 模式每次都会写
        GetUpdate._poll_count += 1
        debug_log(f'长轮询: timeout={self.timeout}s')
        if GetUpdate._poll_count % 10 == 1:
            log(f'长轮询, timeout={self.timeout}s')
        try:
            data = {
                'get_updates_buf': self.cursor,
                'client_id': self.client_id,
                'base_info': {"channel_version": "2.0.0"}
            }
            resp = requests.post(url=url, headers=headers, json=data, timeout=self.timeout)
            debug_log(f'长轮询响应: {resp.text}')
            with open(REQUEST_JSON_FILE,'w',encoding='utf-8') as f:
                json.dump(resp.json(),f,indent=2)
            if resp.json().get('msgs'):
                state = resp.status_code
                self.body = resp.json()
                # 更新游标
                self.config['cursor'] = self.body.get('get_updates_buf')
                self.cursor = self.config['cursor']
                save_clawbot_config(self.config)
            else:
                self.resp = False
                return None
                
        except requests.exceptions.ReadTimeout:
            self.resp = False
            return None

        if state != 200:
            log(f'状态码错误: {state}')
        else:
            debug_log(f'cursor: {self.cursor}')
            self.resp = True
            return self.body

    # @property
    # def msg(self):
    #     return self.getupdates()
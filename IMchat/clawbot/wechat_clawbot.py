import qrcode
import requests
import time
import threading
import queue
import uuid
from debug.log import *
from nobot.src.common import *
from message.wechat.wechat_in import WechatIn
from IMchat.clawbot.wechat_common import *

class WechatClawbot:

    def __init__(self):
        self.config = load_clawbot_config()
        self.uin = random_wechat_uin()
        self.base_url = 'https://ilinkai.weixin.qq.com'
        self.token = self.token_check()
        self.client_id = self.config.get('clientid', str(uuid.uuid4()))

    def fetch_qr(self):
        """获取登录二维码，返回 (qr_code_str, 是否成功)"""
        log('获取QR...')
        url = f"{self.base_url}/ilink/bot/get_bot_qrcode?bot_type=3"

        debug_log(f"请求QR URL: {url}, headers: {make_base_headers(self.uin)}")
        
        re_qr = requests.get(url, headers=make_base_headers(self.uin))

        debug_log(f"QR请求响应状态: {re_qr.status_code}, 内容: {re_qr.text}")

        if re_qr.status_code != 200:
            log(f'请求失败: {re_qr.status_code}')
            return None, False
        data = re_qr.json()
        log(str(data))
        qr = data.get('qrcode')
        if not qr:
            log(f'未获取到二维码: {data}')
            return None, False
        qr_url = data.get('qrcode_img_content')
        print(f"请用微信扫码: {qr_url}")
        # 终端打印二维码
        img = qrcode.QRCode(border=1)
        img.add_data(qr_url)
        img.make(fit=True)
        img.print_ascii(invert=True)
        return qr, True


    def poll_qr_status(self, url):
        """轮询二维码扫码状态"""
        try:
            log('轮询检测QR状态...')
            resp = requests.get(url, headers=make_base_headers(self.uin))
            debug_log(resp.text)
            if resp.status_code != 200:
                print(f"轮询请求失败: {resp.status_code}")
                return None
            return resp.json()
        except requests.exceptions.ConnectionError:
            log('连接断开,重试...')
            return None
        except requests.exceptions.ReadTimeout:
            log('等待...')
            return None

    # ========== 消息收发 ==========
    # 由WechatIn类对象接收,WechatOut类对象发送


    # qr
    def fst_log_in(self):
        qr_queue = queue.Queue()
        # 获取 QR
        def get_qr_thread_target():
            qr, ok = self.fetch_qr()
            if ok:
                qr_queue.put(qr)

        th = threading.Thread(target=get_qr_thread_target)
        th.start()
        qr = qr_queue.get()
        th.join()

        # 轮询扫码状态
        while True:
            state = self.poll_qr_status(
                f'{self.base_url}/ilink/bot/get_qrcode_status?qrcode={qr}'
            )
            if state:
                status = state.get('status')
                if status == 'confirmed':
                    log('confirmed, 退出轮询...')
                    connection = state
                    break
                elif status == 'expired':
                    log('超时, 重新获取QR...')
                    th = threading.Thread(target=get_qr_thread_target)
                    th.start()
                    qr = qr_queue.get()
                    th.join()
                    log('获取完毕')
                log(f'状态检测: {status}')

        # 保存登录信息
        self.config['baseurl'] = connection.get('baseurl', self.base_url)
        self.config['token']   = connection.get('bot_token', '')
        self.config['botid']   = connection.get('ilink_bot_id', '')
        self.config['userid']  = connection.get('ilink_user_id', '')
        self.base_url = connection.get('baseurl', self.base_url)
        save_clawbot_config(self.config)
        log('存储登录信息...')

    # ---- token 校验 ----
    def token_check(self):
        log('检查token可用性...')
        self.config = load_clawbot_config()
        debug_log(f'当前token: {self.config.get("token", "")}')
        token = self.config.get('token', '')
        if not token:
            log('没有已存储的token信息, 扫码登录...')
            self.fst_log_in()
            log('登录完毕, 等待服务器同步session(3秒)...')
            time.sleep(3)
            log('重载token...')
            self.config = load_clawbot_config()
            token = self.config['token']
            log('验证token...')

        resp = requests.post(
            url=f'{self.base_url}/ilink/bot/getconfig',
            headers=make_auth_headers(token, self.uin),
            json={
                'ilink_user_id': self.config['userid'],
                'context_token': '',
                'base_info': {"channel_version": "2.0.0"}
            }
        )
        debug_log(resp.text)
        try:
            if resp.json()['errcode'] == -14:
                log('会话过期error, 将删除目前存储的token并尝试重新获取...')
                self.config['token'] = ''
                save_clawbot_config(self.config)
                self.fst_log_in()
        except KeyError:
            pass

        if resp.status_code == 200:
            log('已存储的token可用!')
        else:
            log(f'已存储的token不可用({resp.status_code}), 扫码登录...')
            self.fst_log_in()
            log('登录完毕')
        return self.config['token']


    # ========== 主入口 ==========

    def wechat_claw(self):
        
        debug_log('尝试创建 WechatIn 对象')
        wechat_msg = WechatIn(
            self.config,
            self.token,
        )
        log('开始运行...')
        wechat_msg.loop_run()
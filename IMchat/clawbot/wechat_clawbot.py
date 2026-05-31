import qrcode
import requests
import time
import threading
import queue
import uuid
from debug.log import *
from nobot.src.common import *
from message.clawbot.wechatmsg import WechatBotMessage
from IMchat.clawbot.wechat_common import *
from IMchat.clawbot.getmsg.getupdate import GetUpdate
from IMchat.clawbot.getmsg.handlemsg import Handle
from IMchat.clawbot.sendmsg.send import Sender
from IMchat.clawbot.getmsg.waitimer import Witimer
from IMchat.clawbot.getmsg.replymsg import get_msg_reply

class WechatClawbot:

    def __init__(self):
        self.config    = load_clawbot_config()
        self.uin       = random_wechat_uin()
        self.baseurl   = 'https://ilinkai.weixin.qq.com'
        self.token     = self.token_check()
        self.client_id = self.config.get('clientid', str(uuid.uuid4()))

        self.timeout   = 35

    def fetch_qr(self):
        """获取登录二维码，返回 (qr_code_str, 是否成功)"""
        log('获取QR...')
        url = f"{self.baseurl}/ilink/bot/get_bot_qrcode?bot_type=3"

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
                f'{self.baseurl}/ilink/bot/get_qrcode_status?qrcode={qr}'
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
        self.config['baseurl'] = connection.get('baseurl', self.baseurl)
        self.config['token']   = connection.get('bot_token', '')
        self.config['botid']   = connection.get('ilink_bot_id', '')
        self.config['userid']  = connection.get('ilink_user_id', '')
        self.baseurl = connection.get('baseurl', self.baseurl)
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
            url=f'{self.baseurl}/ilink/bot/getconfig',
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
        
        debug_log('创建启动对象')
        log('开始运行...')
        msgobj = WechatBotMessage() #消息对象 存储消息信息 消息提交处理后重建
        waitimer = None
        while True:
            Updater = GetUpdate(self.timeout) #每次循环新建接收器并传入timeout
            Updater.getupdates() #长轮询接收消息
            msgobj.msgtext = Updater.msgtext

            if msgobj.msgtext is None: #无消息
                if msgobj.msglist == [] and msgobj.medialist == []:
                    debug_log('轮询超时,下一次轮询...')
                    continue
            else: 
                #有消息接收 → 提取内容 → 设定等待
                fetcher = Handle(Updater, len(msgobj.msglist) + 1)
                fetcher.fetch()
                debug_log(vars(fetcher))
                msgobj.msgtext  = fetcher.msgtext
                msgobj.msgtype  = fetcher.msgtype
                msgobj.media    = fetcher.media if fetcher.media is not None else msgobj.media
                msgobj.msglist      += fetcher.msglist
                msgobj.medialist     += fetcher.medialist
                msgobj.context_token  = fetcher.context_token
                msgobj.msgnum        += 1

                waitimer = Witimer(msgobj, fetcher.process_now)
                if waitimer.set_waitime():
                    pass  # 命令类消息 → 不等待，直接处理
                else:
                    self.timeout = waitimer.timeout
                    continue

            # === 处理已积累的消息（超时提交 或 命令类直接处理）===
            if waitimer is None:
                continue
            msgobj.msgtext = waitimer.msgtext
            msgobj.msgtype = waitimer.msgtype
            msgobj.media   = waitimer.media
            replyout_obj   = get_msg_reply(msgobj)

            sender = Sender(replyout_obj) #消息发送器
            sender.send()
            msgobj = WechatBotMessage()
            self.timeout = 35
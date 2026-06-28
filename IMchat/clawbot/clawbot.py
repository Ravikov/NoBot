import time
import threading
import uuid
from debug.log import *
from nobot.src.common import *
from message.clawbot.clawbotmsg import *
from IMchat.clawbot.clawbot_common import *
from IMchat.clawbot.login import ClawBotLogin
from IMchat.clawbot.getmsg.getupdate import GetUpdate
from IMchat.clawbot.getmsg.handlemsg import Handle
from IMchat.clawbot.getmsg.waitimer import Waitimer
from IMchat.clawbot.sendmsg.send import Sender
from IMchat.clawbot.sendmsg.sendtyping import Typing

from nobot.user.user import usrobj

class WechatClawbot:

    def __init__(self):
        self.uin       = random_wechat_uin()
        self.baseurl   = 'https://ilinkai.weixin.qq.com'
        login          = ClawBotLogin()
        self.token     = login.token_check()
        self.config    = load_clawbot_config()
        del login
        self.usr       = WechatBotUsr(self.config['userid'], self.config.get('name','main'), self.config['token'])
        self.client_id = self.config.get('clientid', str(uuid.uuid4()))
        self.botconfig = load_config()

    # ========== 消息收发 ==========
    # 由WechatIn类对象接收,WechatOut类对象发送

    # ========== 主入口 ==========

    @staticmethod
    def set_msglist(msgobj):
        log(str(msgobj.msglist))
        if not msgobj.msglist == []:
            log(f'提交消息接收,共{msgobj.msgnum}条')

            if len(msgobj.msglist) == 1 and msgobj.medialist == []:
                msgobj.msgtext = msgobj.msglist[0] # 单条文本消息
                msgobj.media   = []
                msgobj.msgtype = 1

            elif len(msgobj.msglist) == 1 and msgobj.medialist != []:
                msgobj.msgtext = msgobj.msglist[0]
                msgobj.msgtype = msgobj.medialist[0]['type'] # 单条媒体消息
                msgobj.media   = msgobj.medialist

            else:
                msgobj.msgtext = msgobj.msglist
                msgobj.media   = msgobj.medialist
                msgobj.msgtype = 9 # 队列消息

            log(f'最终消息: {msgobj.msgtext}')
            return msgobj

    def wechat_claw(self):
        
        debug_log('创建启动对象')
        log('开始运行...')
        updater  = GetUpdate(self.usr)
        msgobj   = WechatBotMessage()
        handler = Handle(usrobj=self.usr)

        while 1:
            process_now = False
            # 主循环            
            updater.getupdates() #长轮询接收消息
            if updater.resp:
                log('收到消息')
                handler.msgobj = msgobj
                handler.body   = updater.body
                handler.fetch()
                msgobj = handler.msgobj # 交换消息对象
                msgobj.msgtime = time.time()

                if handler.process_now:
                    process_now = True
                else:
                    waitimer = Waitimer(msgobj)
                    waitimer.set_waitime()
                    updater.timeout = waitimer.timeout

                    msgobj.msgnum += 1
                    debug_log(f'消息对象状态: {vars(msgobj)}')
                    continue
            if msgobj.msgtime is not None or process_now:
                if not process_now:
                    try:
                        process_now = time.time() - msgobj.msgtime >= updater.timeout
                    except TypeError:
                        pass
                if process_now:
                    # 显示正在输入提示用户开始处理
                    log('提示输入中')
                    def get_typing(): #临时函数
                        typing = Typing(msgobj, self.usr)
                        typing.get_config()
                        typing.send_typing()
                    threading.Thread(target=get_typing).start()

                    log('提交处理...')
                    msgobj = self.set_msglist(msgobj) #设定消息列表和类型
                    replyout_obj = msgobj.get_msg_reply()
                    debug_log(f'发送消息 {replyout_obj.msgtext}')
                    sender = Sender(replyout_obj, self.usr)
                    sender.send()
                    msgobj = WechatBotMessage() #重置消息对象
                    updater.timeout = 35
            else:
                debug_log('轮询超时,下一次轮询...')
                debug_log('get_config维持链接...')
                threading.Thread(target=Typing(msgobj, self.usr).get_config).start()
                
                continue

        # 旧逻辑参考
        # msgobj = WechatBotMessage() #消息对象 存储消息信息 消息提交处理后重建
        # waitimer = None
        # while True:
        #     Updater = GetUpdate(self.timeout) #每次循环新建接收器并传入timeout
        #     Updater.getupdates() #长轮询接收消息
        #     msgobj.msgtext = Updater.msgtext

        #     if msgobj.msgtext is None: #无消息
        #         if msgobj.msglist == [] and msgobj.medialist == []:
        #             debug_log('轮询超时,下一次轮询...')
        #             continue
        #     else: 
        #         #有消息接收 → 提取内容 → 设定等待
        #         fetcher = Handle(Updater, len(msgobj.msglist) + 1)
        #         fetcher.fetch()
        #         debug_log(vars(fetcher))
        #         msgobj.msgtext  = fetcher.msgtext
        #         msgobj.msgtype  = fetcher.msgtype
        #         msgobj.media    = fetcher.media if fetcher.media is not None else msgobj.media
        #         msgobj.msglist      += fetcher.msglist
        #         msgobj.medialist     += fetcher.medialist
        #         msgobj.context_token  = fetcher.context_token
        #         msgobj.msgnum        += 1

        #         waitimer = Witimer(msgobj, fetcher.process_now)
        #         if waitimer.set_waitime():
        #             pass  # 命令类消息 → 不等待，直接处理
        #         else:
        #             self.timeout = waitimer.timeout
        #             continue

        #     # === 处理已积累的消息（超时提交 或 命令类直接处理）===
        #     if waitimer is None:
        #         continue
        #     msgobj.msgtext = waitimer.msgtext
        #     msgobj.msgtype = waitimer.msgtype
        #     msgobj.media   = waitimer.media
        #     replyout_obj   = get_msg_reply(msgobj)

        #     sender = Sender(replyout_obj) #消息发送器
        #     sender.send()
        #     msgobj = WechatBotMessage()
        #     self.timeout = 35
# 目前包含三种常规启动方式
# webhook
# wechat(个人号,不可用)
# wechat_clawbot
# websocket开发中
# import asyncio
# import websocket
from flask import Flask,request
from debug.log import log
from nobot.src.core.get_reply.reply import reply
from nobot.src.common import *


# ==========<各种启动方式>==========
# 创建一个flask应用
app = Flask(__name__)

# ----------webhook启动----------
# flask装饰器webhook的使用
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    mes = None 

    if data.get("post_type") == 'message':
        mes = data["message"][0]["data"]["text"]
        log(f'消息格式正确,用户输入: {mes}')
    else:
        log('忽略错误格式')

    result,ms = reply({'type': 1,'msg': mes})

    return {"reply":result}

# ----------微信个人账号启动----------
# 不可用的微信服务...
def wechat_bot():
    log('服务不可用,请退出')
    # import itchat
    # from itchat.content import TEXT

    # @itchat.msg_register(TEXT)
    # def handle_msg(msg):
    #     user_msg = msg['Text']
    #     log(f'收到微信消息: {user_msg}')
    #     # 你的 reply 返回 (result, ms)，我们只要 result
    #     reply_text, _ = reply(user_msg)
    #     log(f'微信回复: {reply_text[:50]}')
    #     return reply_text

    # log('微信Bot启动，扫码登录...')
    # itchat.auto_login(hotReload=True, enableCmdQR=2)
    # log('登录成功，开始处理消息')
    # itchat.run()

#----------微信clawbot接入----------
# 详见对应模块
    

# ----------websocket的实现----------

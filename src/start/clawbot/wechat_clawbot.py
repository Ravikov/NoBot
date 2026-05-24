import qrcode
import random
import base64
import requests
import time
import threading
import queue
import json
import uuid
from Crypto.Cipher import AES
from debug.log import log
from src.reply import reply
from src.common import *
from src.touch_llm import sec_llm


# ========== 模块级工具函数（从原 wechat_claw() 体内提级）==========

def load_clawbot_config():
    """读取 wechat_clawbot 配置文件"""
    with open(CLAWBOT_FILE, "r", encoding='utf-8') as f:
        return json.load(f)


def save_clawbot_config(config_dict):
    """写入 wechat_clawbot 配置文件"""
    with open(CLAWBOT_FILE, "w", encoding='utf-8') as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=2)


def random_wechat_uin():
    """生成随机的微信 UIN"""
    rand = random.randint(1, 2**32 - 1)
    return base64.b64encode(str(rand).encode()).decode()


def make_base_headers(uin):
    """创建不含 token 的请求头"""
    return {
        'Content-Type': 'application/json',
        'AuthorizationType': 'ilink_bot_token',
        'X-WECHAT-UIN': uin
    }


def make_auth_headers(token, uin):
    """创建含 Bearer token 的请求头"""
    return {
        'Content-Type': 'application/json',
        'AuthorizationType': 'ilink_bot_token',
        'Authorization': 'Bearer ' + token,
        'X-WECHAT-UIN': uin
    }


def fetch_qr(base_url, uin):
    """获取登录二维码，返回 (qr_code_str, 是否成功)"""
    log('获取QR...')
    url = f"{base_url}/ilink/bot/get_bot_qrcode?bot_type=3"
    re_qr = requests.get(url, headers=make_base_headers(uin))
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


def poll_qr_status(url, uin):
    """轮询二维码扫码状态"""
    try:
        log('轮询检测QR状态...')
        resp = requests.get(url, headers=make_base_headers(uin))
        log(resp.text)
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


def download_media(full_url, token, uin):
    """从 CDN 下载多媒体文件，返回二进制内容或 None (Edited by DeepSeek TUI)"""
    log('从cdn获取多媒体文件...')
    resp = requests.get(url=full_url, headers=make_auth_headers(token, uin))
    log(f'CDN下载状态码: {resp.status_code}')
    if resp.status_code != 200:
        log(f'CDN下载失败: {resp.status_code}, 响应: {resp.text[:200]}')
        return None
    if not resp.content:
        log('CDN下载内容为空')
        return None
    log(f'CDN下载成功, 大小: {len(resp.content)} bytes')
    return resp.content


def unlock_media(aeskey, media, ext='jpg'):
    """AES-ECB 解密多媒体数据并返回 base64 (Edited by DeepSeek TUI)
    aeskey: hex 字符串(32字符,16字节密钥) 或 base64(解码后是 hex 字符串)
    media:  bytes, CDN 下载的加密数据
    ext:    文件扩展名(仅用于日志,默认 jpg)
    返回:   base64 编码的解密数据, 失败返回 None"""
    if media is None:
        log('解密失败: 媒体数据为空', 'Warn')
        return None
    log('原始key:' + aeskey)
    log('开始解码多媒体文件')
    try:
        key = bytes.fromhex(aeskey)
    except ValueError:
        try:
            key_hex = base64.b64decode(aeskey).decode('ascii')
            key = bytes.fromhex(key_hex)
            log('密钥为 base64 编码 hex')
        except Exception as e:
            log(f'密钥解码失败: {e}', 'Warn')
            return None
    log(f'AES密钥长度: {len(key)} bytes')
    cipher = AES.new(key, AES.MODE_ECB)
    unlocked = cipher.decrypt(media)
    log(f'{ext} 解密后数据长度: {len(unlocked)} bytes')

    # PKCS7 unpad 验证 (Edited by DeepSeek TUI)
    ful_len = unlocked[-1]
    if ful_len < 1 or ful_len > 16:
        log(f'PKCS7 padding 长度异常: {ful_len}, 可能密钥错误或数据损坏', 'Warn')
        return None
    if unlocked[-ful_len:] != bytes([ful_len]) * ful_len:
        log('PKCS7 padding 验证失败, 可能密钥错误或数据损坏', 'Warn')
        return None

    data = unlocked[:-ful_len]
    log(f'去除padding后数据长度: {len(data)} bytes')
    return base64.b64encode(data).decode('utf-8')


# ========== 消息收发 ==========

def fetch_one_message(token, uin, client_id, config_dict, base_url,timeout=35):
    """长轮询获取一条消息
    返回: (msg_text, msg_type, to_user, context_token) 或 (None, None, None, None)"""
    headers = make_auth_headers(token, uin)
    url = f'{base_url}/ilink/bot/getupdates'
    log('长轮询等待消息接收...')
    state = 0  # 初始值, 防止未绑定 (Edited by DeepSeek TUI)
    while True:
        try:
            cursor = config_dict['cursor']
            data = {
                'get_updates_buf': cursor,
                'client_id': client_id,
                'base_info': {"channel_version": "2.0.0"}
            }
            resp = requests.post(url=url, headers=headers, json=data, timeout=timeout)
            # log(resp.text)
            if resp.json().get('msgs'):
                state = resp.status_code
                body = resp.json()
                # 更新游标
                config_dict['cursor'] = body.get('get_updates_buf')
                save_clawbot_config(config_dict)
                break
        except requests.exceptions.ReadTimeout:
            return None, None, None, None

    if state != 200:
        log(f'状态码错误: {state}')
        return None, None, None, None

    msg_type = body['msgs'][0]['item_list'][0]['type']
    # 文本消息
    if msg_type == 1:
        msg = body['msgs'][0]['item_list'][0]['text_item']['text']
    # 图片/视频消息处理 (Edited by DeepSeek TUI)
    elif msg_type in [2,5]:
        if msg_type == 2:
            aeskey = body['msgs'][0]['item_list'][0]['image_item']['aeskey']
            url = body['msgs'][0]['item_list'][0]['image_item']['media']['full_url']
            media = download_media(url, token, uin)
            msg = unlock_media(aeskey, media, ext='jpg')
        elif msg_type == 5:
            aeskey = body['msgs'][0]['item_list'][0]['video_item']['media']['aes_key']
            url = body['msgs'][0]['item_list'][0]['video_item']['media']['full_url']
            if not body['msgs'][0]['item_list'][0]['video_item'].get('media'):
                log('视频媒体数据为空', 'Warn')
                msg = ''
            else:
                media = download_media(url, token, uin)
                msg = unlock_media(aeskey, media, ext='mp4')
    else:
        msg = ''
        log(f'未知消息类型: {msg_type}', 'Warn')

    to_user = body['msgs'][0]['from_user_id']
    context_token = body['msgs'][0]['context_token']
    return msg, msg_type, to_user, context_token


def send_reply_messages(result, to_user, context_token, config_dict):
    """发送回复消息（分条发送）(Edited by DeepSeek TUI)"""
    token = config_dict['token']
    base_url = config_dict['baseurl']
    uin = random_wechat_uin()  # 发送消息时重新生成 UIN

    # 获取 ticket 并申请打字状态
    def get_ticket():
        log('获取ticket...')
        resp = requests.post(
            url=f'{base_url}/ilink/bot/getconfig',
            headers=make_auth_headers(token, uin),
            json={
                'ilink_user_id': config_dict['userid'],
                'context_token': context_token
            }
        )
        if resp.status_code == 200:
            return resp.json()['typing_ticket']

    def send_typing(ticket):
        log('申请打字状态...')
        resp = requests.post(
            url=f'{base_url}/ilink/bot/sendtyping',
            headers=make_auth_headers(token, uin),
            json={
                'ilink_user_id': config_dict['userid'],
                'typing_ticket': ticket,
                'status': 1
            }
        )
        if resp.status_code == 200:
            log('打字状态申请成功')

    ticket = get_ticket()
    n = 1
    if result['type'] == 1:
        log(f'回复类型: text, 总条数: {len(result["msg"])}')
        for msg in result['msg']:
            if msg == ' ':
                continue
            threading.Thread(target=send_typing, args=(ticket,)).start()
            time.sleep(0.5)
            text_token = context_token if n == 1 else ''
            data = {
                "msg": {
                    "from_user_id": '',
                    "to_user_id": to_user,
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
            resp = requests.post(
                f'{base_url}/ilink/bot/sendmessage',
                headers=make_auth_headers(token, uin),
                json=data
            )
            time.sleep(2)
            log(resp.text)
            if resp.status_code == 200 and resp.json() == {}:
                log('本条消息发送成功')
                n += 1
            else:
                ret = resp.json().get('ret', '?')
                log(f'发送失败, 状态码: {resp.status_code}, 返回码: {ret}')
                return 1
    log('所有消息发送完毕')


# ========== 主入口 ==========

def wechat_claw():
    config_dict = load_clawbot_config()
    log('获取client_id...')
    if config_dict.get('clientid', ''):
        CLIENT_ID = config_dict['clientid']
    else:
        CLIENT_ID = str(uuid.uuid4())
        config_dict['clientid'] = CLIENT_ID
        save_clawbot_config(config_dict)

    BASE_URL = config_dict.get('baseurl', 'https://ilinkai.weixin.qq.com')
    UIN = random_wechat_uin()

    # ---- QR 登录相关 ----
    qr_queue = queue.Queue()

    def fst_log_in():
        nonlocal config_dict, BASE_URL
        # 获取 QR
        def get_qr_thread_target():
            qr, ok = fetch_qr(BASE_URL, UIN)
            if ok:
                qr_queue.put(qr)

        th = threading.Thread(target=get_qr_thread_target)
        th.start()
        qr = qr_queue.get()
        th.join()

        # 轮询扫码状态
        while True:
            state = poll_qr_status(
                f'https://ilinkai.weixin.qq.com/ilink/bot/get_qrcode_status?qrcode={qr}',
                UIN
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
        config_dict['baseurl'] = connection.get('baseurl', BASE_URL)
        config_dict['token']    = connection.get('bot_token', '')
        config_dict['botid']    = connection.get('ilink_bot_id', '')
        config_dict['userid']   = connection.get('ilink_user_id', '')
        BASE_URL = connection.get('baseurl', BASE_URL)
        save_clawbot_config(config_dict)
        log('存储登录信息...')

    # ---- token 校验 ----
    def token_check():
        nonlocal config_dict, BASE_URL
        log('检查token可用性...')
        config_dict = load_clawbot_config()
        token = config_dict.get('token', '')
        if not token:
            log('没有已存储的token信息, 扫码登录...')
            fst_log_in()
            log('登录完毕, 等待服务器同步session(3秒)...')
            time.sleep(3)
            log('重载token...')
            config_dict = load_clawbot_config()
            token = config_dict['token']
            log('验证token...')

        resp = requests.post(
            url=f'{BASE_URL}/ilink/bot/getconfig',
            headers=make_auth_headers(token, UIN),
            json={
                'ilink_user_id': config_dict['userid'],
                'context_token': '',
                'base_info': {"channel_version": "2.0.0"}
            }
        )
        log(resp.text)
        try:
            if resp.json()['errcode'] == -14:
                log('会话过期error, 将删除目前存储的token并尝试重新获取...')
                config_dict['token'] = ''
                save_clawbot_config(config_dict)
                fst_log_in()
        except KeyError:
            pass

        if resp.status_code == 200:
            log('已存储的token可用!')
        else:
            log(f'已存储的token不可用({resp.status_code}), 扫码登录...')
            fst_log_in()
            log('登录完毕')
        return config_dict['token']

    # ---- 消息处理 & 回复 ----
    def handle_and_reply(msg, msg_type, to_user, context_token, media=None):
        if msg_type == 1:
            log('生成回复...')
            result, ms = reply({'type': 1, 'msg': msg})
        elif msg_type == 2:
            log('处理图片消息...')
            result, ms = reply({'type': 2, 'msg': msg})
        elif msg_type == 5:
            log('处理视频消息...')
            result, ms = reply({'type': 5, 'msg': msg})
        elif msg_type == 9:
            log('处理队列消息...')
            result,ms = reply({'type': 9, 'msg': msg, 'media': media})
        else:
            log('不支持的格式!', 'Warn')
            return 1
        if result['type'] == 1:  # 正常回复 (Edited by DeepSeek TUI)
                send_reply_messages(result, to_user, context_token, config_dict)
        else:
            log('LLM 回复失败', 'Warn')

    # ---- 主循环 ----
    def loop_run():
        token = token_check()
        msg_list = []
        history = load_history()
        media = []
        n_media = 1
        timeout = 35
        while True:
            n = 0
            TO = config_dict['userid']
            msg, msg_type, to_user, context_token = fetch_one_message(
                token, UIN, CLIENT_ID, config_dict, BASE_URL, timeout=timeout
            )
            if msg_type == 1:
                log(f'消息监听get: {msg}, 类型: {msg_type}')
                msg_list.append(msg)
                if msg[0] == '/':
                    msg_list = [msg]
                    msg = None
            if msg_type in [2,5]:
                if msg_type == 2:
                    msg_type_desc = '图片'
                elif msg_type == 5:
                    msg_type_desc = '视频'
                log(f'消息监听get: <{msg_type_desc}消息>')
                msg_list.append(f'<{msg_type_desc}消息{n_media}>')
                n_media += 1
                media.append({'type': msg_type, 'media': msg})
                msg = f'<{msg_type_desc}消息>'
            if msg:
                log('调用模型判断等待...')
                waitime = sec_llm(
                    0.8,
                    [{
                        'role':'system',
                        'content':"""判断本条消息需要等待下一条输入的时间(1~50),无论如何都要给以等待时间,
                                    仅回复整数,不能包含任何其他内容,你需要推测用户行为来判断等待时间,例如拍摄照片要多等一会，
                                    如:用户输入了"我拍了一张照片",你可以判断用户可能在拍照并等待照片上传,
                                    这时你可以回复几十秒来让程序多等待一会(一般大于30),照片上传完成后再继续处理消息.
                                    用户输入了'我在想一个问题',你可以判断用户可能在思考,
                                    这时你也可以让程序多等待一会(建议大于20)再处理消息.
                                    用户输入'等一下','稍等','等等'这一类时,也要稍微增加等待时间(建议5~15)来提升用户体验.
                                    其他诸如'对了','我突然想起来',''我还有件事'等可能一切引发用户连续输入的消息,适当增加等待时间来提升用户体验.
                                    禁止回复0和负数,要根据用户的行为来判断合理的等待时间,
                                    如果用户某条消息需要等待他发下一条,你回复了1或者2,程序就会马上处理消息,这会导致用户还没想好就被打断,
                                    但是过长的等待又会造成用户干等,体验下降,所以多数一般性问题建议在5~15为最佳,
                                    所以请用合理的等待时间提升用户体验.
                                    不要太小也不要太大,合理判断!!!"""
                    }]+
                    [{
                        'role':'system',
                        'content':f'<过往消息列表>{(msg_list)}<本条消息内容>{msg}'
                    }]+
                    history['history']+
                    history['memory']+
                    [{
                        'role':'user',
                        'content':f''
                    }]
                )
                log(f'判断结果: {waitime}')
                try:
                    waitime = int(waitime)
                    log(f'等待{waitime}秒')
                except:
                    log('返回有误')
                    waitime = 0
                timeout = config['wait'] + waitime
                log(f'设置下一轮轮询超时时间为{timeout}秒')
                n += 1
            else:
                log(str(msg_list))
                if not msg_list == []:
                    log(f'提交消息接收,共{n}条')
                    if len(msg_list) == 1 and media == []:
                        msg = msg_list[0] # 单条文本消息
                        msg_type = 1
                    elif len(msg_list) == 1 and media != []:
                        msg_type = media[0]['type'] # 单条媒体消息
                    else:
                        msg = msg_list
                        msg_type = 9 # 队列消息
                    handle_and_reply(msg, msg_type, TO, context_token, media=media)
                    timeout = 35

    loop_run()

import qrcode
import random
import base64
import requests
import time
import threading
import queue
import json
import uuid
from debug.log import log
from src.reply import reply
from src.common import *

def wechat_claw():
    def load_config():
        with open(CLAWBOT_FILE,"r",encoding='utf-8') as f:
            wechat_clawbot = json.load(f)
        return wechat_clawbot
    
    wechat_clawbot_config = load_config()
    log('获取client_id...')
    if wechat_clawbot_config['clientid'] != '':
        CLIENT_ID = wechat_clawbot_config['clientid']
    else:
        CLIENT_ID = str(uuid.uuid4())
        wechat_clawbot_config['clientid'] = CLIENT_ID
        with open(CLAWBOT_FILE,'w',encoding='utf-8') as f:
            json.dump(wechat_clawbot_config,f,ensure_ascii=False,indent=2)

    BASE_URL = 'https://ilinkai.weixin.qq.com'
    def random_wechat_uin():
        rand = random.randint(1,2**32-1)
        return base64.b64encode(str(rand).encode()).decode()
    
    UIN = random_wechat_uin()

    # 两种headers的创建
    def set_headers():
        headers = {
            'Content-Type': 'application/json',
            'AuthorizationType': 'ilink_bot_token',
            'X-WECHAT-UIN': UIN
        }
        return headers
    
    def set_headers_with_token(token):
        headers = {
            'Content-Type': 'application/json',
            'AuthorizationType': 'ilink_bot_token',
            'Authorization': 'Bearer '+token,
            'X-WECHAT-UIN': UIN
        }
        return headers

    # 子线程获取QR防止阻断并使用queue得到返回结果
    qr_queue = queue.Queue()
    def get_qr():
        log('获取QR...')
        url = f"{BASE_URL}/ilink/bot/get_bot_qrcode?bot_type=3"
        re_qr = requests.get(
            url,
            headers=set_headers()
        )

        if re_qr.status_code != 200:
            log(f'请求失败: {re_qr.status_code}')
            return None
        
        data = re_qr.json()
        log(str(data))
        qr = data.get('qrcode')
        if not qr:
            log(f'未获取到二维码: {data}')
            return None
        
        qr_url = data.get('qrcode_img_content')
        
        print(f"请用微信扫码: {qr_url}")
        qr_queue.put(qr)
        qr = qrcode.QRCode(border=1)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)  # 直接打印到终端
        
    # QR状态检测函数
    def get_qrcode_status(url):
        try:
            log('轮询检测QR状态...')
            response = requests.get(url,headers=set_headers())
            log(response.text)
            
            if response.status_code != 200:
                print(f"轮询请求失败: {response.status_code}")
                return None
            
            return response.json()  # 返回解析后的 JSON 字典
        except requests.exceptions.ReadTimeout:
            log('等待...')
            return None

    # 无token启动
    def fst_log_in():
        nonlocal wechat_clawbot_config
        get_qr_th = threading.Thread(target=get_qr)
        get_qr_th.start()
        qr = qr_queue.get()
        get_qr_th.join()
        connection = None
        # 长轮询获取QR状态更新
        while 1:
            state = get_qrcode_status(f'https://ilinkai.weixin.qq.com/ilink/bot/get_qrcode_status?qrcode={qr}')
            if state:
                status = state.get('status')
                if status == 'confirmed':
                    log('confirmed,推出轮询...')
                    connection = state
                    break
                elif status == 'expired':
                    log('超时,重新获取QR...')
                    get_qr_th = threading.Thread(target=get_qr)
                    get_qr_th.start()
                    qr = qr_queue.get()
                    get_qr_th.join()
                    log('获取完毕')
                else:
                    pass
                log(f'状态检测: {status}')

        # 存储信息方便复用
        def save_conect_mes(connection):
            nonlocal BASE_URL
            wechat_clawbot = load_config()
            wechat_clawbot['baseurl'] = connection.get('baseurl')
            wechat_clawbot['token'] = connection.get('bot_token')
            wechat_clawbot['botid'] = connection.get('ilink_bot_id')
            wechat_clawbot['userid'] = connection.get('ilink_user_id')
            BASE_URL = connection.get('baseurl')
            with open(CLAWBOT_FILE,"w",encoding='utf-8') as f:
                json.dump(wechat_clawbot,f,ensure_ascii=False,indent=2)

        wechat_clawbot_config = load_config()
        log('存储登录信息...')
        save_conect_mes(connection)

    # 核查token可用状态/存在状态
    def token_check():
        nonlocal wechat_clawbot_config
        log('检查token可用性...')
        wechat_clawbot_config = load_config()
        token = wechat_clawbot_config['token']
        if not token:
            log('没有已存储的token信息,扫码登录...')
            fst_log_in()
            log('登录完毕,等待服务器同步session(3秒)...')
            time.sleep(3)
            log('重载token...')
            wechat_clawbot_config = load_config()
            token = wechat_clawbot_config['token']
            log('验证token...')
        re = requests.post(
            url=f'{BASE_URL}/ilink/bot/getupdates',
            headers=set_headers_with_token(token),
            json={
                'get_updates_buf': wechat_clawbot_config['cursor'],
                'client_id': CLIENT_ID,
                'timeout_ms': 3000,
                'base_info': { 
                    "channel_version": "2.0.0"
                }
            }
            )
        log(re.text)
        try:
            a = re.json()['errcode']
            if a == -14:
                log('会话过期error,将删除目前存储的token并尝试重新获取...')
                wechat_clawbot_config['token'] = ''
                with open(CLAWBOT_FILE,"w",encoding='utf-8') as f:
                    json.dump(wechat_clawbot_config,f,ensure_ascii=False,indent=2)
                fst_log_in()
            s = False
        except KeyError:
            s = True
        if re.status_code == 200 and s:
            log('已存储的token可用!')
        else:
            log(f'已存储的token不可用({re.status_code}),扫码登录...\n如果多次出现该日志,请检查是否有其他错误或问题')
            fst_log_in()
            log('登录完毕')
        return token

    # getupdate长轮询收取消息
    def get_mes(token):
        headers = set_headers_with_token(token)
        url = f'{BASE_URL}/ilink/bot/getupdates'
        log('长轮询等待消息接收...')
        while 1:
            try:
                cursor = wechat_clawbot_config['cursor']
                data = {
                    # 游标
                    'get_updates_buf': cursor,
                    'client_id': CLIENT_ID,
                    'base_info': {
                        "channel_version": "2.0.0"
                    }
                }
                response = requests.post(url=url,headers=headers,json=data)
                # log(response.text)
                if response.json()['msgs'] != []:
                    state = response.status_code
                    response = response.json()
                    wechat_clawbot_config['cursor'] = response.get('get_updates_buf')
                    with open('config/wechat_clawbot.json','w',encoding='utf-8') as f:
                        json.dump(wechat_clawbot_config,f,ensure_ascii=False,indent=2)
                    break
            except requests.exceptions.ReadTimeout:
                pass
        if state == 200:
            mes_type = response['msgs'][0]['item_list'][0]['type']
            mes = response['msgs'][0]['item_list'][0]['text_item']['text']
            to_user = response['msgs'][0]['from_user_id']
            context_token = response['msgs'][0]['context_token']
            # log(context_token)
            
            return mes,mes_type,to_user,context_token
        else:
            log(f'状态码错误: {response.status_code}')
        return None

    def get_llm_reply(mes):
        result,ms = reply(mes)
        if result != 1:
            return result
        else:
            return None

    def send_mes(result,to_user,context_token):
        # 对方正在输入的提示
        def get_ticket():
            log('获取ticket...')
            get_config = requests.post(
                url=f'{BASE_URL}/ilink/bot/getconfig',
                headers=set_headers_with_token(wechat_clawbot_config['token']),
                json={
                    'ilink_user_id': wechat_clawbot_config['userid'],
                    'context_token': context_token
                }
            )
            if get_config.status_code == 200:
                ticket = get_config.json()['typing_ticket']
                return ticket
            else:
                pass
        def send_type(ticket):
            log('申请打字状态...')
            send_typing = requests.post(
                url=f'{BASE_URL}/ilink/bot/sendtyping',
                headers=set_headers_with_token(wechat_clawbot_config['token']),
                json={
                    'ilink_user_id': wechat_clawbot_config['userid'],
                    'typing_ticket': ticket,
                    'status': 1
                }
            )
            if send_typing.status_code == 200:
                log('打字状态申请成功')

        ticket = get_ticket()

        # log(context_token)
        n = 0
        for msg in result:
            if result != ' ':
                threading.Thread(target=send_type,args=(ticket,)).start()
                time.sleep(0.5)
                if n == 0:
                    text_token = context_token
                else:
                    text_token = ''
                data = {
                    "msg": {
                        "from_user_id": '',
                        "to_user_id": to_user,
                        "context_token": text_token,
                        "message_type": 2,
                        "message_state": 2,
                        "client_id": str(uuid.uuid4()),
                        "item_list": [
                        {
                            "type": 1,
                            "text_item": {"text": msg}
                        }
                        ],
                        'base_info': { 
                            "channel_version": "2.0.0"
                        }
                    }
                }
                # log(f"完整请求: {json.dumps(data, ensure_ascii=False)}") 
                log(f'发送消息: {msg}')
                token = wechat_clawbot_config['token']
                re = requests.post(
                    f'{BASE_URL}/ilink/bot/sendmessage',
                    headers=set_headers_with_token(token),
                    json=data
                )
                time.sleep(2)
                log(re.text)
                if re.status_code == 200 and re.json() == {}:
                    log('本条消息发送成功')
                else:
                    ret = re.json()['ret']
                    log(f'发送失败,状态码: {re.status_code} , 返回码: {ret}')
                    return 1
        log('所有消息发送完毕')

    # 调用函数
    def re_and_send(mes,mes_type,to_user,context_token):
        if mes_type == 1:
            log('生成回复...')
            result = get_llm_reply(mes)
            send_mes(result,to_user,context_token)
        else:
            log('不支持的格式!','warn')
            send_mes('格式不支持!')

    # 循环接收和发送消息
    def loop_run(token):
        while 1:
            while 1:
                mes,mes_type,to_user,context_token = get_mes(token)
                if mes:
                    break
            log(f'消息监听get: {mes},类型: {mes_type}')
            re_and_send(mes,mes_type,to_user,context_token)

    # 入口函数
    def start_wechat_clawbot():
        token = token_check()
        loop_run(token)
        
    start_wechat_clawbot()
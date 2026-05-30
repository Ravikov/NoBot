import base64
import requests
# import io
# from PIL import Image
from debug.log import log
from nobot.src.core.get_reply.touch_llm import sec_llm
from Crypto.Cipher import AES
from nobot.src.common import *
from message.wechat.wechat_out import WechatOut
from message.msg import *
from debug.log import *
from IMchat.clawbot.wechat_common import save_clawbot_config, random_wechat_uin, make_auth_headers

# 子类 接收wechatbot消息
class WechatIn(Message):
    baseurl = 'https://ilinkai.weixin.qq.com'

    def __init__(self, config, token):
        super().__init__(msgtype=None, msgtext=None, fromusr='wechatbot', media=None)
        self.msglist = []          # 消息列表,包含多条消息
        self.botconfig = load_config()
        self.config = config
        self._token = token         # 微信clawbot的token
        self._context_token = None  # 微信clawbot上下文token
        self._to_user = None        # 消息发送目标用户ID
        self._media_url = None      # 多媒体消息的CDN链接
        self._media = None          # 多媒体消息加密内容
        self.medialist = []         # 多媒体消息列表,包含多个媒体
        self._media_key = None      # 多媒体消息的AES解密密钥
        self.timeout = 35           # 长轮询超时时间
        self.uin = random_wechat_uin() # 随机uin
        self.cursor = config.get('cursor', '') # 消息游标
        self.client_id = None       # 随机client_id,亦可读取配置文件
        self.msgtime = None         # 消息时间戳

    # 媒体消息处理
    def download_media(self):
        """从 CDN 下载多媒体文件，返回二进制内容或 None (Edited by DeepSeek TUI)"""
        log('从cdn获取多媒体文件...')
        debug_log(f'CDN URL: {self._media_url}')
        resp = requests.get(url=self._media_url, headers=make_auth_headers(self._token, self.uin))
        log(f'CDN下载状态码: {resp.status_code}')
        if resp.status_code != 200:
            log(f'CDN下载失败: {resp.status_code}, 响应: {resp.text[:200]}')
            return None
        if not resp.content:
            log('CDN下载内容为空')
            return None
        log(f'CDN下载成功, 大小: {len(resp.content)} bytes')
        return resp.content

    # def compress_image(image_bytes, max_size_mb=0.7):
    #     """压缩图片到指定大小（MB）以下"""
    #     img = Image.open(io.BytesIO(image_bytes))
    #     if img.mode == 'RGBA':
    #         img = img.convert('RGB')
        
    #     max_bytes = int(max_size_mb * 1024 * 1024)
    #     quality = 85
    #     while quality > 10:
    #         buffer = io.BytesIO()
    #         img.save(buffer, format='JPEG', quality=quality, optimize=True)
    #         if buffer.tell() <= max_bytes:
    #             return buffer.getvalue()
    #         quality -= 10
    #     # 保底：缩尺寸
    #     ratio = (max_bytes / buffer.tell()) ** 0.5
    #     img.thumbnail((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    #     buffer = io.BytesIO()
    #     img.save(buffer, format='JPEG', quality=75, optimize=True)
    #     return buffer.getvalue()

    def unlock_media(self,ext='jpg'):
        """AES-ECB 解密多媒体数据并返回 base64 (Edited by DeepSeek TUI)
        aeskey: hex 字符串(32字符,16字节密钥) 或 base64(解码后是 hex 字符串)
        media:  bytes, CDN 下载的加密数据
        ext:    文件扩展名(仅用于日志,默认 jpg)
        返回:   base64 编码的解密数据, 失败返回 None"""
        if self._media is None:
            log('解密失败: 媒体数据为空', 'Warn')
            return None
        debug_log('原始key:' + self._media_key)
        log('开始解码多媒体文件')
        try:
            key = bytes.fromhex(self._media_key)
        except ValueError:
            try:
                key_hex = base64.b64decode(self._media_key).decode('ascii')
                key = bytes.fromhex(key_hex)
                log('密钥为 base64 编码 hex')
            except Exception as e:
                log(f'密钥解码失败: {e}', 'Warn')
                return None
        debug_log(f'AES密钥长度: {len(key)} bytes')
        cipher = AES.new(key, AES.MODE_ECB)
        unlocked = cipher.decrypt(self._media)
        debug_log(f'{ext} 解密后数据长度: {len(unlocked)} bytes')

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

        # # 如果图片太大，压缩
        # if len(data) > 900000:  # 超过 0.9 MB
        #     print(f"原图大小: {len(data)} bytes，开始压缩...")
        #     data = self.compress_image(data, target_size_mb=0.7)

        return base64.b64encode(data).decode('utf-8')

    # 接收消息
    def fetch(self):
        """长轮询获取一条消息
        返回: {'msg': ,'msg_type': ,'to_user': ,'context_token': } 或 None"""
        headers = make_auth_headers(self._token, self.uin)
        url = f'{self.baseurl}/ilink/bot/getupdates'
        log('长轮询等待消息接收...')
        state = 0  # 初始值, 防止未绑定
        try:
            data = {
                'get_updates_buf': self.cursor,
                'client_id': self.client_id,
                'base_info': {"channel_version": "2.0.0"}
            }
            debug_log(f'长轮询请求URL: {url}, headers: {headers}, data: {data}, timeout: {self.timeout}')
            resp = requests.post(url=url, headers=headers, json=data, timeout=self.timeout)
            debug_log(resp.text)
            if resp.json().get('msgs'):
                state = resp.status_code
                body = resp.json()
                # 更新游标
                self.config['cursor'] = body.get('get_updates_buf')
                self.cursor = self.config['cursor']
                save_clawbot_config(self.config)
            else:
                return None
        except requests.exceptions.ReadTimeout:
            return None

        if state != 200:
            log(f'状态码错误: {state}')
            return None

        self.msgtype = body['msgs'][0]['item_list'][0]['type']
        debug_log(f'接收消息类型: {self.msgtype}')
        # 文本消息
        if self.msgtype == 1:
            self.msgtext = body['msgs'][0]['item_list'][0]['text_item']['text']
        # 图片/视频消息处理 (Edited by DeepSeek TUI)
        elif self.msgtype in [2,5]:
            if self.msgtype == 2:
                aeskey = body['msgs'][0]['item_list'][0]['image_item']['aeskey']
                url = body['msgs'][0]['item_list'][0]['image_item']['media']['full_url']
                self._media_url = url
                self._media_key = aeskey
                self._media = self.download_media()
                self._media = self.unlock_media(ext='jpg')
            elif self.msgtype == 5:
                aeskey = body['msgs'][0]['item_list'][0]['video_item']['media']['aes_key']
                url = body['msgs'][0]['item_list'][0]['video_item']['media']['full_url']
                if not body['msgs'][0]['item_list'][0]['video_item'].get('media'):
                    log('视频媒体数据为空', 'Warn')
                else:
                    self._media_url = url
                    self._media_key = aeskey
                    self._media = self.download_media()
                    self._media = self.unlock_media(ext='mp4')
        else:
            log(f'未知消息类型: {self.msgtype}', 'Warn')

        self.context_token = body['msgs'][0]['context_token']
        get_msg = {
            'type': self.msgtype,
            'msg': self.msgtext,
            'to_user': self.config['userid'],
            'context_token': self.context_token,
            'media': None
        }
        debug_log(f'接收消息: {get_msg}')
        return get_msg
    
    def llm_reply(self):
        debug_log(f'reply输入消息: {self.msgtext}, 类型: {self.msgtype}')
        get = ReplyIn(self.msgtype, self.msgtext, media = self._media)
        return get.get_reply()

    # ---- 消息处理 & 回复 ----
    def handle_and_reply(self):
        if self.msgtype == 1:
            log('生成回复...')
            result = self.llm_reply()
        elif self.msgtype == 2:
            log('处理图片消息...')
            result = self.llm_reply()
        elif self.msgtype == 5:
            log('处理视频消息...')
            result = self.llm_reply()
        elif self.msgtype == 9:
            log('处理队列消息...')
            result = self.llm_reply()
        else:
            log('不支持的格式!', 'Warn')
            return 1
        debug_log(f'reply输出结果: {result.get_info()}')
        return result


    # ----------------------------------------
    # ----------循环消息接收(程序主循环)----------
    # ----------------------------------------

    def loop_run(self):
        history = load_history()
        
        while True:
            self.msgtext = None
            self.msgtype = None
            self._media = None
            self.msgtime = None
            n_media = 1
            n = 0
            result = self.fetch()
            if self.msgtime is not None:
                if time.time() - self.msgtime < self.timeout:
                    timeouted = False
                else:
                    timeouted = True
                    log('已达等待时间')
            else:
                timeouted = False
            if not timeouted:
                if self.msgtext is None and self._media is None:
                    log('等待超时, 继续轮询...')
                    continue

            if self.msgtext:
                P = False
            else:
                P = True
            if self.msgtype == 1 and not P:
                log(f'消息监听get: {self.msgtext}, 类型: 1')
                self.msglist.append(self.msgtext)
                if self.msgtext[0] == '/':
                    self.msglist = [self.msgtext,]
                    self.msgtext = None
                    P = True # 跳过后续决策
            elif self.msgtype in (2, 5):
                type_desc = '图片' if self.msgtype == 2 else '视频'
                log(f'消息监听get: <{type_desc}消息>')
                self.msglist.append(f'<{type_desc}消息{n_media}>')
                self.medialist.append({'type': self.msgtype, 'media': self._media})
                self.msgtext = f'<{type_desc}消息>'
                n_media += 1
            elif P:
                pass
            else:
                log(f'未知消息类型: {self.msgtype}', 'Warn')
                continue
            
            if not P:
                self.msgtime = time.time()
                debug_log(f'消息时间戳 {self.msgtime}')
                n += 1
                if self.botconfig['llm_decide_wait']:
                    log('调用模型判断等待...')
                    waitime = sec_llm(
                        0.5,
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
                            'content':f'<过往消息列表>{(self.msglist[:-1])}<本条消息内容>{self.msgtext}'
                        }]+
                        history['history']+
                        history['memory']+
                        [{'role':'user','content':''}]
                    )
                    log(f'判断结果: {waitime}')
                    try:
                        waitime = int(waitime)
                        log(f'等待{waitime}秒')
                    except:
                        log('返回有误')
                        waitime = 0
                else:
                    waitime = 0
                timeout = self.botconfig['wait'] + waitime
                if timeout < self.botconfig['wait']:
                    timeout = self.botconfig['wait']
                elif timeout < 0:
                    timeout = 0
                log(f'设置下一轮轮询超时时间为{timeout}秒')
                self.timeout = timeout
                self.msgtext = None
                self.msgtype = None
                self._media = None
                n += 1
                log(self.msglist)
            
            else:
                log(str(self.msglist))
                if not self.msglist == []:
                    log(f'提交消息接收,共{n}条')
                    if len(self.msglist) == 1 and self.medialist == []:
                        self.msgtext = self.msglist[0] # 单条文本消息
                        self.msgtype = 1
                    elif len(self.msglist) == 1 and self.medialist != []:
                        self.msgtext = self.msglist[0]
                        self.msgtype = self.medialist[0]['type'] # 单条媒体消息
                    else:
                        self.msgtext = self.msglist
                        self._media = self.medialist
                        self.msgtype = 9 # 队列消息
                    self._to_user = self.config['userid']
                    log(f'最终消息列表: {self.msgtext}')
                    result = self.handle_and_reply()
                    if result != 1:
                        WechatOut(result, self._token, self._context_token, self._to_user).send()
                    else:
                        log('消息内容为空,略过')
                    history = load_history()
                    self.timeout = 35
                    self.msglist = []
                    # self.msglist = []
                    # self.msgtext = None
                    self.medialist = []
                    # self.msgtype = None
                    # self.msgtime = None
                    # n = 1

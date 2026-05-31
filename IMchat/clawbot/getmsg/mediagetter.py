import base64
import requests
# import io
# from PIL import Image
from Crypto.Cipher import AES
from message.clawbot.wechatmsg import WechatBotMessage
from debug.log import *
from IMchat.clawbot.wechat_common import make_auth_headers

class MediaGetter(WechatBotMessage):

    def __init__(self, url, key, ext='jpg'):
        super().__init__()
        self.media_url = url
        self.media_key = key
        self.ext = ext

    # 媒体消息处理
    def download_media(self):
        """从 CDN 下载多媒体文件，返回二进制内容或 None (Edited by DeepSeek TUI)"""
        log('从cdn获取多媒体文件...')
        debug_log(f'CDN URL: {self.media_url}')
        resp = requests.get(url=self.media_url, headers=make_auth_headers(self.token, self.uin))
        log(f'CDN下载状态码: {resp.status_code}')
        if resp.status_code != 200:
            log(f'CDN下载失败: {resp.status_code}, 响应: {resp.text[:200]}')
            return None
        if not resp.content:
            log('CDN下载内容为空')
            return None
        log(f'CDN下载成功, 大小: {len(resp.content)} bytes')
        self.media = resp.content

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

    def unlock_media(self):
        """AES-ECB 解密多媒体数据并返回 base64 (Edited by DeepSeek TUI)
        aeskey: hex 字符串(32字符,16字节密钥) 或 base64(解码后是 hex 字符串)
        media:  bytes, CDN 下载的加密数据
        ext:    文件扩展名(仅用于日志,默认 jpg)
        返回:   base64 编码的解密数据, 失败返回 None"""
        if self.media is None:
            log('解密失败: 媒体数据为空', 'Warn')
            return None
        debug_log('原始key:' + self.media_key)
        log('开始解码多媒体文件')
        try:
            key = bytes.fromhex(self.media_key)
        except ValueError:
            try:
                key_hex = base64.b64decode(self.media_key).decode('ascii')
                key = bytes.fromhex(key_hex)
                log('密钥为 base64 编码 hex')
            except Exception as e:
                log(f'密钥解码失败: {e}', 'Warn')
                return None
        debug_log(f'AES密钥长度: {len(key)} bytes')
        cipher = AES.new(key, AES.MODE_ECB)
        unlocked = cipher.decrypt(self.media)
        debug_log(f'{self.ext} 解密后数据长度: {len(unlocked)} bytes')

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

        self.media = base64.b64encode(data).decode('utf-8')
    
    def getter(self):
        self.download_media()
        self.unlock_media()
        return self.media
import base64
import random
import json
from nobot.src.common import CLAWBOT_FILE

# 配置文件读写
def load_clawbot_config():
    """读取 wechat_clawbot 配置文件"""
    with open(CLAWBOT_FILE, "r", encoding='utf-8') as f:
        return json.load(f)

def save_clawbot_config(config):
    """写入 wechat_clawbot 配置文件"""
    with open(CLAWBOT_FILE, "w", encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

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
from message.msg import ReplyIn
from debug.log import *

def get_msg_reply(msgobj):
    """传入wechat消息对象交由reply处理"""
    debug_log(vars(msgobj))
    replyout = ReplyIn(msgobj).get_reply()
    replyout.context_token = msgobj.context_token
    return replyout # ReplyOut消息对象(额外添加c_t属性)
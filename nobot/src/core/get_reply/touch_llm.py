import requests
import json
import time
from nobot.src.common import *
from debug.log import log


class TouchLLM:
    """大模型api调用,传入msg,llm代号"""
    """
    result格式:
    {
    'msg': 消息正文,
    'type': ,
    'origin_resp': 响应内容,
    'delay': 响应延迟,指令消息为0,错误为-1
    }
    """
    # line82-result

    def __init__(self, msg, llm, tpe=1, sysmsg=None, tem=0, search=False):
        # llm: API,secAPI,searchAPI,multimodalAPI
        self.usrmsg  = msg
        self.sysmsg  = sysmsg
        self.llm     = llm
        self.postmsg = '' # 模型收到的消息
        self.max_tokens = 2048
        self.tem     = tem
        self.search  = search
        self.tpe     = tpe
        self.config  = load_config()
        
        self.hit_rate = 0
        self.result  = {}

        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            self.role_prompt = f.read()

    @retry
    def get_result(self):
        
        headers = {
            "Authorization": f'Bearer {self.config[self.llm]["key"]}',
            "Content-Type": "application/json"
        }

        if self.llm != 'multimodalAPI':
            data = {
                "model": self.config[self.llm]['name'],
                "messages": self.postmsg,
                "max_tokens": self.max_tokens,
                "temperature": self.tem,
                "enable_web_search": self.search,
                "thinking": {"type": "disabled"}
            }
        else:
            if self.tpe == 2:
                msg = '描述本张图片,忽略水印内容,除非用户要求.如果图中有文字信息,你应该准确的识别并写出来,比如一道数学题你要写出题目内容,如果有几何图形你也应该准确描述这个图形'
                media_content = {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{self.usrmsg}'}}
            else:
                msg = '描述本条视频的内容,按照不换行的json格式标明内容时间位置及对应画面,重要部分请详细描述.若有文字信息也应准确描述'
                media_content = {'type': 'video_url', 'video_url': {'url': f'data:video/mp4;base64,{self.usrmsg}'}}
            data = {
                "model": self.config[self.llm]['name'],
                "messages": [{
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': msg},
                        media_content
                        ]
                    }],
                "max_tokens": self.max_tokens,
                "temperature": self.tem
            }
            
        debug_log(f"headers:{headers},data:{data}")
        resp = requests.post(
            json=data,
            headers=headers,
            url=self.config[self.llm]['url']
            )
        
        log('状态码校验')
        if resp.status_code == 200:
            log('状态码正确')
            with open(RESPONSEJSON_FILE,'w',encoding='utf-8') as f:
                json.dump(resp.json(),f,ensure_ascii=False,indent=2)
            result = resp.json()
            llm_msg = result['choices'][0]['message']['content']
            try:
                total_token = result['usage']['total_tokens']
                hit_token   = result['usage']['prompt_cache_hit_tokens']
                hit_rate    = f"{hit_token / total_token * 100:.1f}%"
                log(f'总token:{total_token},缓存命中:{hit_token},命中率 {hit_rate}')
                if self.config['debug']:
                    self.hit_rate = hit_rate
            except:
                pass
            
            if self.config['debug'] and self.llm=='API':
                llm_msg += f"#缓存命中率: {self.hit_rate}"
            self.result = {
                    'msg': llm_msg,
                    'type': 1,
                    'origin_resp': resp.text,
                    'delay': resp.elapsed.total_seconds()
                }
        else:
            match resp.status_code:
                case 404:
                    err_dscrb = '连接错误 404 NotFound,检查您API的url是否正常'
                case 400:
                    err_dscrb = '请求错误,通常是由于程序自身问题'
                case 401:
                    err_dscrb = '验证错误,请确保您的API有正确的key'
                case _:
                    err_dscrb = '您可以自行搜索错误码'
            log(f'状态码错误:{resp.status_code},{err_dscrb},响应:{resp.text}')
            self.result = {
                    'msg': f"""大模型调用出现问题,请参考日志文件.
完整响应: {resp.text}
错误描述: 状态码错误:{resp.status_code}:{err_dscrb}""",
                    'type': 1,
                    'origin_resp': resp.text,
                    'delay': -1
                }
    
    # 构建回复postmsg
    def get_postmsg(self):
        history = load_history()
        return (
                    [{"role": "system", "content": self.role_prompt}]
                    + [{"role": "system", "content": '回答长度稍长时必须使用#符号对你的回答进行分段(仅在两段交界处且#后方不要加空格)除非该场景下长文段对话体验更好,段数不限,不允许出现换行,不允许出现动作描述'}]
                    + history.get('history', [])
                    + history.get('memory', [])
                    + [{"role": "system",
                        "content": "对话格式举例,非用户消息与上下文,仅作回复格式参考: 用户:你好. AI:你好#需要我帮助你做什么呢#我可以满足你的很多请求"}]
                    + [{"role": "user", "content": self.usrmsg}]
                    + self.get_time()
                )

    def touch(self):
        match self.llm:
            case 'API':
                self.postmsg = self.get_postmsg()
                self.tem = self.config['temperature']
                self.max_tokens = 4096
            case 'secAPI':
                self.postmsg = self.sysmsg
            case 'searchAPI':
                self.postmsg = self.get_postmsg()
                self.tem = self.config['temperature']
                self.max_tokens = 4096
            case 'multimodalAPI':
                self.postmsg = self.usrmsg

            case _:
                debug_log('传参错误!')
        self.get_result()
                
    def get_time(self):
        if self.config['or_time_feel']:
            return [
                {'role':'system','content':f"当前时间:{time.strftime('%Y-%m-%d %H:%M', time.localtime())}"}
                ]
        else:
            return []
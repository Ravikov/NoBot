import requests
import json
import time
from nobot.src.common import *
from debug.log import log


class TouchLLM:
    """大模型api调用,传入msg,llm代号"""
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
                msg = '描述本张图片,忽略水印内容,除非用户要求'
                media_content = {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{self.usrmsg}'}}
            elif self.tpe == 5:
                msg = '描述本条视频的内容,按照不换行的json格式标明内容时间位置及对应画面,重要部分请详细描述'
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
                json.dump(resp.json(),f,indent=2)
            result = resp.json()
            llm_msg = result['choices'][0]['message']['content']
            try:
                total_token = result['usage']['total_tokens']
                hit_token   = result['usage']['prompt_cache_hit_tokens']
                log(f'总token:{total_token},缓存命中:{hit_token},命中率 {hit_token/total_token}')
            except:
                pass

            self.result = {
                    'msg': llm_msg,
                    'type': 1,
                    'origin_resp': resp.text,
                    'delay': resp.elapsed.total_seconds()
                }
        else:
            match resp.status_code:
                case 404:
                    err_dscrb = '连接错误 404 NotFound'
                case 400:
                    err_dscrb = '请求错误'
                case _:
                    err_dscrb = ''
            log(f'状态码错误:{resp.status_code},{err_dscrb},响应:{resp.text}')
    
    # 构建回复postmsg
    def get_postmsg(self):
        history = load_history()
        return (
                    [{"role": "system", "content": self.role_prompt}]
                    + [{"role": "system", "content": '回答长度稍长时必须使用#符号对你的回答进行分段(仅在两段交界处)除非该场景下长文段对话体验更好,段数不限,不允许出现换行,不允许出现动作描述'}]
                    + history.get('history', [])
                    + history.get('memory', [])
                    + self.get_time()
                    + [{"role": "user", "content": self.usrmsg}]
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
                {'role':'system','content':f"当前时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"}
                ]
        else:
            return []
import requests
import json
import time
from nobot.src.common import *
from debug.log import log
from nobot.src.core.llm.retry import retry


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

    def __init__(self, msg, llm, tpe=1, sysmsg=None, tem=0, search=False, action_dscrb=''):
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

        self.action_dscrb  = action_dscrb
        
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
            
        if self.llm == 'multimodalAPI':
            debug_log(f'请求多模态API: model={self.config[self.llm]["name"]}, 媒体大小={len(self.usrmsg) if self.usrmsg else 0} chars')
        else:
            debug_log(f"请求API: model={self.config[self.llm]['name']}")
        timeout = 60 if self.llm == 'multimodalAPI' else 30
        resp = requests.post(
            json=data,
            headers=headers,
            url=self.config[self.llm]['url'],
            timeout=timeout
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
            
            # 缓存命中率注入
            if self.config['debug'] and self.llm=='API' and self.tpe != 101:
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
                    'msg': f"""大模型{self.config[self.llm]['name']}调用出现问题,请参考日志文件.
---------------
完整响应: {resp.text}
---------------
错误描述: 状态码错误:{resp.status_code}:{err_dscrb}
---------------
模型配置信息: {self.config[self.llm]}
""",
                    'type': 1,
                    'origin_resp': resp.text,
                    'delay': -1
                }
    
    # 构建回复postmsg
    def get_postmsg(self):
        history = load_history()
        debug_log(f"tpe= {self.tpe}")

        if self.tpe == 1:
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
        elif self.tpe == 101:
            debug_log("使用esp32提示词")
            self.tem = 0.2
            return (
                        [{"role": "system", "content": self.role_prompt}]
                        + [{"role": "system", "content": """
你可以控制一块esp32开发板,你的回复格式必须严格遵循如下json格式,且禁止以md代码块包裹,不要出现任何json格式以外的任何内容:
{
"msg":这里是你要说的话,字符串,
"action":这里是你要做的动作,具体可以做哪些动作会在下文提示词告诉你,以动作对应的编号回复,整数,
"hardware":这里是你的动作要作用的对象,下文提示词也会给出可用的硬件,注意与action相对应,同样回复编号,整数,
"show":这里是你要呈现在屏幕上的文字,要注意显示屏仅支持英文,故此条应为英文字符串,若硬件存在本字段尽量不要省略,
"delay":此项可以包含一个延迟,用于表示本字典与下一字典的延迟执行时间,0表示不等待,-1表示等待当前指令执行完毕(即依次执行),任意整数表示延迟时间(秒)
"angle":当你需要控制舵机时,在这里填入需要达到的角度,整数
}
某些情况下你可以收到图片描述,故不应表示自己无法接收图片
如果需要执行多个指令,可以将各个字典用#号分开,第二个往后的动作字典不包含msg字段,所有msg在首个字典中呈现
msg中的消息可以用$分开,实现分段回复
对于动作键值对,如果无需实现动作或用户指定的动作或硬件不存在则填充-1
show字段仅在硬件列表包含屏幕时出现,填充"off"(小写)表示关闭屏幕(仅在用户要求的情况下)
不包含delay字段时程序默认为0,仅执行一条指令时不包含delay字段,最后一条指令字典也不包含delay
"""}]
                        + [{"role": "system", "content": f"可用的action及硬件:{self.action_dscrb}"}]
                        + history.get('history', [])
                        + history.get('memory', [])
                        + [{"role": "system",
                            "content": """对话格式举例,非用户消息与上下文,仅作回复格式参考,具体可用硬件与动作以实际为准.
用户:点亮红色led.
AI:{
"msg":"好的,已点亮",
"action":0,
"hardware":0
}"""}]
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
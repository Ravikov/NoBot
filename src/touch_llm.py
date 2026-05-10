import requests
import json
import time
from src.common import *
from debug.log import log

with open(PROMPT_FILE,"r",encoding="utf-8") as f:
    role_prompt = f.read()

# api post函数
def api_post(headers,data,url):
    response = requests.post(
        url=url,
        headers=headers,
        json=data,
        timeout=20  # 超时时间，防止卡死
    )
    return response

def connect(key,url,model,messages,tem=0,max_tokens=2048,search=False):
    # 准备headers
    headers = {
        "Authorization": f'Bearer {key}',  # 证明你有权限调用
        "Content-Type": "application/json"     # 告诉服务器：我发给你的Body是JSON格式
    }

    # 创建data
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": tem,
        "enable_web_search": search,
        "thinking": {"type": "disabled"}
    }

    # 发出post请求
    response = api_post(headers,data,url)
    if response.status_code == 200:
        return response,200
    else:
        log(response.text)
        log('状态码错误: '+str(response.status_code))
        return 1,response.status_code

# 调用函数
def get_re(key,url,model,messages,tem=0,max_tokens=2048,search=False):
    response,state = connect(key,url,model,messages,tem,max_tokens,search)

    # log(response.text)
    # 将结果写入json文件
    if state == 200:
        orgin_result = response.json()
        with open(RESPONSEJSON_FILE,'w',encoding = 'UTF-8') as f:
                json.dump(orgin_result, f, ensure_ascii=False, indent=2)
        # 输出status和延迟信息
        state = response.status_code
        ms = response.elapsed.total_seconds()
        # 提取json文件中的有效部分
        result = orgin_result["choices"][0]["message"]["content"]

        total_tokens = orgin_result["usage"]["total_tokens"]
        cache_hit_tokens = orgin_result.get("usage")
        cache_hit_tokens = cache_hit_tokens.get("prompt_cache_hit_tokens",'None')

        with open(STATEJSON_FILE,'r',encoding='UTF-8') as f:
            tokens = json.load(f)
        all_tokens = tokens.get("all_tokens") + total_tokens
        tokens["all_tokens"] = all_tokens
        with open(STATEJSON_FILE,'w',encoding='UTF-8') as f:
            json.dump(tokens,f,ensure_ascii=False,indent=2)
        
        log('调用结束...')
        log(f'模型token使用...总tokens: {total_tokens},缓存命中: {cache_hit_tokens},累计tokens: {all_tokens}')

        return result,state,ms,orgin_result
    else:
        return 1,state,1,1
    
def get_time():
    if config['or_time_feel']:
            now_time = [{"role":"system","content":f"当前时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"}]
    else:
        now_time = []
    return now_time

# 调用主api函数
def fst_llm(question):
    # 读取记忆并拼接message
    history = load_history()
    messages = [{"role": "system", "content": role_prompt}]+[{"role": "system", "content": '必须使用#符号对你的回答进行分段(仅在两段交界处),段数不限,不允许出现换行,不允许出现动作描述'}]+history.get('history')+history.get('memory')+get_time()+[{"role": "user", "content": question}]
    result,state,ms,orgin_result = get_re(config['API']['key'],config['API']['url'],config['API']['name'],messages,config['temperature'],config['max_tokens'])
    return result,state,ms,orgin_result

# 辅助api调用函数
def sec_llm(tem,mes):
    messages = mes
    result,state,ms,orgin_result = get_re(config['secAPI']['key'],config['secAPI']['url'],config['secAPI']['name'],messages,tem,4096)

    log('辅助模型完成调用')
    sec_result = result
    return sec_result

# 联网搜索模型
def search_api(mes):
    history = load_history()
    messages = [{"role": "system", "content": role_prompt}]+[{"role": "system", "content": '必须使用#符号对你的回答进行分段(仅在两段交界处),段数不限,不允许出现换行,不允许出现动作描述'}]+history.get('history',[])+history.get('memory',[])+get_time()+[{"role": "user", "content": mes}]
    result,state,ms,orgin_result = get_re(config['searchAPI']['key'],config['searchAPI']['url'],config['searchAPI']['name'],messages,config['temperature'],config['max_tokens'],True)
    log('联网搜索模型完成调用')
    
    return result,state,ms,orgin_result
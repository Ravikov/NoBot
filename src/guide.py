# 配置文件编辑引导
# 需要配置的项目:
# 主模型url,key,name
# 辅助模型三要素
# 联网模型三要素
# 可选项:
# 角色提示词(难以通过命令行实现)
# 主模型温度
# 最大上下文轮数
import json
import shutil
from .common import *
from debug.log import log

def set_llm(llm,project):
    print('请按要求输入配置内容,键入 N 表示此项保持不变')
    project_value = input(f'请设置{llm}的{project}: ')
    if project_value not in ['N','n','']:
        with open('config/config.json','r',encoding='utf-8') as f:
            config = json.load(f)
        if llm == '主模型':
            llm = 'API'
        elif llm == '辅助模型':
            llm = 'secAPI'
        elif llm == '联网模型':
            llm = 'searchAPI'
        config[llm][project] = project_value
        with open('config/config.json','w',encoding='utf-8') as f:
            json.dump(config,f,ensure_ascii=False,indent=2)
        print('配置已写入')

def set_mainllm(project):
    print('请按要求输入配置内容,键入 N 或 直接Enter 表示此项保持不变')
    with open('config/config.json','r',encoding='utf-8') as f:
                config = json.load(f)
    if project == 'temperature':
        value = input(f'请设置主模型参数[{project}](0~2之间的整数,默认1.2,当前{config["temperature"]}): ')
        project = 'temperature'
    elif project == '最大上下文轮数': 
        value = input(f'请设置主模型参数[{project}](默认20,当前{config["max_history_turns"]}): ')
        project = 'max_history_turns'
    elif project == '是否启用时间注入':
        value = (input(f'请设置主模型参数[{project}](true或false,默认true,当前{config["or_time_feel"]}): '))
        project = 'or_time_feel'
    if value not in ['N','n','']:
        if type(value) == str and value not in ['true','True','False','false']:
            value = float(value)
        else:
            value = bool(value)
        config[project] = value
        with open('config/config.json','w',encoding='utf-8') as f:
            json.dump(config,f,ensure_ascii=False,indent=2)
        print('配置已写入')

def set_config():
    input('开始进行配置文件设置,按Enter继续')
    print('进行大模型API配置')
    for m in llm_list:
        for p in project_list:
            set_llm(m,p)
    print('大模型API信息配置完毕')
    print('进行主模型相关配置')
    for p in mainllm_settings:
        set_mainllm(p)
    print('所有基础配置完毕')
    with open('config/config.json','r',encoding='utf-8') as f:
                config = json.load(f)
    config['non_setup'] = False
    with open('config/config.json','w',encoding='utf-8') as f:
        json.dump(config,f,ensure_ascii=False,indent=2)
    print('角色提示词请写入config/role_prompt.txt文件')
    log('备份配置文件...')
    shutil.copy2('./config/config.json','./config/config.json.bak')
    log('备份完毕')
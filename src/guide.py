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

def set_llm(llm,project,or_search):
    if llm == '联网模型':
        if not or_search:
            return 0
    project_value = input(f'请设置{llm}的{project}: ')
    if project_value not in ['N','n','']:
        if llm == '主模型':
            llm = 'API'
        elif llm == '辅助模型':
            llm = 'secAPI'
        elif llm == '联网模型':
            llm = 'searchAPI'
        elif llm == '多模态理解模型':
            llm = 'multimodalAPI'
        elif llm == '生图模型':
            llm = 'imageAPI'
        config[llm][project] = project_value
        with open(CONFIG_FILE,'w',encoding='utf-8') as f:
            json.dump(config,f,ensure_ascii=False,indent=2)
        print('配置已写入')

def set_mainllm(project):
    if project == 'temperature':
        value = input(f'请设置主模型参数[{project}](0~2之间的整数,默认1.0,当前{config["temperature"]}): ')
        project = 'temperature'
    elif project == '最大上下文轮数': 
        value = input(f'请设置主模型参数[{project}](默认20,必须为整数,当前{config["max_history_turns"]}): ')
        project = 'max_history_turns'
    elif project == '是否启用时间注入':
        value = input(f'请设置主模型参数[{project}](true或false,默认true,当前{config["or_time_feel"]}): ')
        project = 'or_time_feel'
    if value not in ['N','n','']:
        if project == 'temperature':
            value = float(value)
        elif project == 'max_history_turns':
            value = int(value)
        elif project == 'or_time_feel':
            value = bool(value)
        config[project] = value
        with open(CONFIG_FILE,'w',encoding='utf-8') as f:
            json.dump(config,f,ensure_ascii=False,indent=2)
        print('配置已写入')

def set_config():
    try:
        input('开始进行配置文件设置,请按要求输入配置内容,键入 N 或 直接Enter 表示此项保持不变,中途可以随时退出,按Enter继续')
        print('进行大模型API配置')
        or_search = input(f'是否启用联网搜索功能?(true或false,默认true,当前{config["or_search"]}): ')
        if or_search not in ['N','n','']:
            if or_search in ['false','False']:
                or_search = False
            else:
                or_search = True
        else:
            or_search = config['or_search']
        config['or_search'] = or_search
        with open(CONFIG_FILE,'w',encoding='utf-8') as f:
            json.dump(config,f,ensure_ascii=False,indent=2)
        for m in llm_list:
            for p in project_list:
                set_llm(m,p,or_search)
        print('大模型API信息配置完毕')
        print('进行主模型相关配置')
        for p in mainllm_settings:
            set_mainllm(p)
        print('所有基础配置完毕')
        config['non_setup'] = False
        with open(CONFIG_FILE,'w',encoding='utf-8') as f:
            json.dump(config,f,ensure_ascii=False,indent=2)
        print('角色提示词请写入config/role_prompt.txt文件')
        log('备份配置文件...')
        shutil.copy2(CONFIG_FILE,CONFIGBAK_FILE)
        log('备份完毕,Ctrl+C退出')
    except EOFError:
        print('\n')
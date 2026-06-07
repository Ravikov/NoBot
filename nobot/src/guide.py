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


# LLM 中文名 → config key 映射
_LLM_KEY_MAP = {
    '主模型': 'API',
    '辅助模型': 'secAPI',
    '联网模型': 'searchAPI',
    '多模态理解模型': 'multimodalAPI',
    '生图模型': 'imageAPI',
}


def set_llm(config, llm, project, or_search):
    """设置单个模型的单个字段，返回修改后的 config"""
    if llm == '联网模型' and not or_search:
        return config
    project_value = input(f'请设置{llm}的{project}: ')
    if project_value not in ['N', 'n', '']:
        key = _LLM_KEY_MAP[llm]
        config[key][project] = project_value
    return config


def set_mainllm(config, project):
    """设置主模型参数，返回修改后的 config"""
    prompts = {
        'temperature': (
            f'请设置主模型参数[temperature](0~2之间的数值,默认1.0,当前{config["temperature"]}): ',
            'temperature',
            float,
        ),
        '最大上下文轮数': (
            f'请设置主模型参数[最大上下文轮数](默认20,必须为整数,当前{config["max_history_turns"]}): ',
            'max_history_turns',
            int,
        ),
        '是否启用时间注入': (
            f'请设置主模型参数[是否启用时间注入](true或false,默认true,当前{config["or_time_feel"]}): ',
            'or_time_feel',
            lambda v: v.lower() == 'true',
        ),
    }
    prompt, key, converter = prompts[project]
    value = input(prompt)
    if value not in ['N', 'n', '']:
        config[key] = converter(value)
    return config


def set_other_params(config):
    """设置其他参数，返回修改后的 config"""
    fields = [
        ('max_tokens', f'请设置其他参数[max_tokens](每次回复最大token数,默认1500,当前{config["max_tokens"]}): ', int),
        ('save_turns', f'请设置其他参数[save_turns](总结记忆后保存的对话轮数,默认10,当前{config["save_turns"]}): ', int),
        ('llm_decide_wait', f'请设置其他参数[llm_decide_wait](让AI决定等待时间,true或false,默认false,当前{config["llm_decide_wait"]}): ', lambda v: v.lower() == 'true'),
        ('wait', f'请设置其他参数[wait](基准等待时间,单位秒,默认8,当前{config["wait"]}): ', int),
        ('debug', f'请设置其他参数[debug](调试模式,true或false,默认false,当前{config["debug"]}): ', lambda v: v.lower() == 'true'),
        ('wash_comma', f'请设置其他参数[wash_comma](替换逗号为空格,true或false,默认false,当前{config["wash_comma"]}): ', lambda v: v.lower() == 'true'),
        ('repeat', f'请设置其他参数[repeat](复读鸡模式,true或false,默认false,当前{config["repeat"]}): ', lambda v: v.lower() == 'true'),
    ]
    for key, prompt, converter in fields:
        value = input(prompt)
        if value not in ['N', 'n', '']:
            config[key] = converter(value)
    return config


def set_config():
    try:
        config = load_config()
        input('开始进行配置文件设置,请按要求输入配置内容,键入 N 或 直接Enter 表示此项保持不变,中途可以随时退出,按Enter继续')

        # —— 联网搜索开关 ——
        print('进行大模型API配置')
        raw = input(f'是否启用联网搜索功能?(true或false,默认true,当前{config["or_search"]}): ')
        if raw not in ['N', 'n', '']:
            config['or_search'] = raw.lower() not in ('false', '0')

        # —— 各模型字段 ——
        for m in llm_list:
            for p in project_list:
                config = set_llm(config, m, p, config['or_search'])
        print('大模型API信息配置完毕')

        # —— 主模型参数 ——
        print('进行主模型相关配置')
        for p in mainllm_settings:
            config = set_mainllm(config, p)

        # —— 其他参数 ——
        print('进行其他参数配置')
        config = set_other_params(config)

        # —— 收尾：一次性写入 + 备份 ——
        config['non_setup'] = False
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print('所有基础配置完毕')
        print('角色提示词请写入config/soul.md文件')
        log('备份配置文件...')
        shutil.copy2(CONFIG_FILE, CONFIGBAK_FILE)
        log('备份完毕,Ctrl+C退出')
    except EOFError:
        print('\n')
# 主函数入口

# 执行前检查
from debug.log import log
from check import check
O = 1
fix_num = check()
if fix_num != 0:
    log('有文件被修复,需要重启主程序,请在程序自动退出后重新运行')
    O = 0

import time
import threading
import sys
import io
import shutil
import os
from src.common import *
from src.touch_llm import *
from src.reply import reply
from src.start.start_ways import *
from src.start.clawbot.wechat_clawbot import *
from src.guide import set_config

# 设置编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==========<测试函数部分>==========
def test(api,url=None,key=None,model=None):
    if api == 0:
        re = connect(key,url,model,[{'role':'user','content':'Just Answer 1'}])
    else:
        re =  connect(config[api]['key'],config[api]['url'],config[api]['name'],[{'role':'user','content':'Just Answer 1'}])
    if re is not None:  # connect 失败时返回 None (Edited by DeepSeek TUI)
        log('测试返回'+re.text)
        re = re.json()
        if re["choices"][0]["message"]["content"] == '1':
            log('模型测试通过')
        else:
            log('测试未通过','warn')
    else:
        log('出错,请检查状态码','error')


# ==========<程序启动部分>==========
# 启动函数
def run_bot():
    if __name__ == '__main__':
        log('程序启动')
        time.sleep(1)
        if config['non_setup']:
            log('首次启动,编辑配置文件...')
            g = input('如果您的配置文件有备份,可以输入"Y"并回车来跳过索引[务必确定您有备份]: ')
            if g in ['Y','y']:
                start_way = 'load'
            else:
                start_way = 'set'
        else:
            print("""启动引导:
                del-清理日志文件
                save-备份配置文件
                load-恢复上一次备份
                set-设置配置文件
                0-测试模型联通(一般会消耗 10 tokens左右)
                1-webhook启动(未维护,不建议使用)
                2-命令行启动
                3-微信启动(不可用)
                4-微信clawbot启动
            """)
            print('在下方输入选择编号并回车,程序运行途中,您可以随时按 CTRL+C 退出,包括现在')
            try:
                start_way = input('>>> ')
            except KeyboardInterrupt:
                log('选择中断')
                return 0
        
        match start_way:
            case '0':
                answer = input(
                    '请输入要测试的模型...\n'
                    '当前可选模型列表:\n'
                    f"1-主模型: {config['API']['name']} , url地址: {config['API']['url']}\n"
                    f"2-辅助模型: {config['secAPI']['name']} , url地址: {config['secAPI']['url']}\n"
                    f"3-联网模型: {config['searchAPI']['name']} , url地址: {config['searchAPI']['url']}\n"
                    '4-亦可键入url,key,modle进行测试\n'
                )
                if answer == '1':
                    test('API')
                elif answer == '2':
                    test('secAPI')
                elif answer == '3':
                    test('searchAPI')
                elif answer == '4':
                    url = input('请输入模型url地址: ')
                    key = input('请输入对应url的API key: ')
                    model = input('请输入模型名: ')
                    test(0,url,key,model)
            case '1':
                # 子线程
                # 1.创建子线程flask启动函数
                def start_flask():
                    log(f'flask子线程开始运行,按Ctrl+C退出程序,线程ID: {flask_work.ident}')
                    log('3秒后启动flask进程...')
                    time.sleep(3)
                    # 启动flask app
                    log('Bot成功唤醒')
                    app.run(host='0.0.0.0',port=5000)
                # 2.创建子进程以规避app.run对日志的阻塞
                flask_work = threading.Thread(target=start_flask,daemon=True)
                flask_work.start()

            case '2':
                log('命令行启动...')
                # 发起请求
                print('循环输入,按ctrl+c可以退出')
                def cmd_start():
                    try:
                        while 1:
                            question = input("请输入问题：")
                            result,ms = reply({'type': 1,'msg':question})
                            print(f'\n请求成功, 返回结果：\n\n{result}\n\n延迟{ms}s')
                            time.sleep(0.5)
                    except EOFError:
                        print('\n')
                threading.Thread(target=cmd_start,daemon=True).start()
            case '3':
                log('微信启动...')
                threading.Thread(target=wechat_bot,daemon=True).start()
            case '4':
                log('Wechat Claw Bot启动...')
                threading.Thread(target=wechat_claw,daemon=True).start()

            case 'set':
                threading.Thread(target=set_config,daemon=True).start()
            case 'save':
                shutil.copy(CONFIG_FILE,CONFIGBAK_FILE)
                log('备份配置文件成功!')
            case 'load':
                shutil.copy(CONFIGBAK_FILE,CONFIG_FILE)
                log('加载配置文件成功!')
            case 'del':
                if input('您确定要删除过往[所有]日志吗? [Y/n]: ') in ['Y','y']:
                    os.remove(ROOT/'debug'/'bot.log')
                    log('过往日志清理完毕')
                else:
                    log('取消清理')

            case _:
                log('输入有误')
    
    return 0

if O:
    try:
        ender = run_bot()
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        log('收到终止指令,2秒后退出...')
        time.sleep(2)
        log("程序优雅退出~")
else:
    ender = 'r'
log(f'程序结束,结束码: {ender}')